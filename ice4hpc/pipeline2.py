import os
import gc
import sys
import time
import psutil

# Some of the “harmless exceptions” are printed because Optuna logs WARNING messages.
# Suppress them by adjusting the logging level so that try-exception does not catch them
import logging
logging.getLogger("optuna").setLevel(logging.ERROR)

import warnings
warnings.filterwarnings("ignore")
import multiprocessing as mp
#mp.set_start_method("spawn", force=True)

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from queue import Queue

import numpy as np
import pandas as pd
from typing import Tuple
from typing import List
from typing import TextIO
from typing import Final

import optuna
import xgboost as xgb
import torch
import torch.nn as nn
from pytorch_tabnet.pretraining import TabNetPretrainer

import matplotlib.pyplot as plt
import seaborn as sns
import umap
from sklearn.cluster import OPTICS
from sklearn.manifold import TSNE
from sklearn.model_selection import KFold, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import PowerTransformer
from sklearn.preprocessing import RobustScaler

# Application features, i.e., HW counters
APP_FEATURES: Final[list[str]] = ['BR_INS','LD_INS','SR_INS','TOT_INS','L1_LDM',
                                  'L1_STM','L2_LDM','L2_STM','FP_SINGLE',
                                  'FP_DOUBLE','ARITH','IO Bytes Read',
                                  'IO Bytes Written','MEM_WCY','Overhead']

# Machine features, i.e., concatenated RAJAPerf results from three settings
MACH_FEATURES: list[str] = []

# Combined machine features for source and target
MACH_COMB_FEATS: list[str] = []

TABNET_BATCH_SIZE: Final[int] = 512

# Number of folds for cross-validation
N_FOLDS: Final[int] = 5

# For multiple rounds of k-fold splitting
N_PRESET_KFOLDS: Final[int] = 5

# Number of optuna trials of objective()
N_OPTUNA_TRIALS: Final[int] = 20

IS_HIP = True

# For reproducible runs
#torch.manual_seed(1357)
#np.random.seed(7913)
#torch.backends.cudnn.deterministic = True
#torch.backends.cudnn.benchmark = False

# -------------------------------------------------------
# Check if a GPU is visible.
# -------------------------------------------------------
def check_gpu():
    cuda_devices = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    if cuda_devices:
        print(f"CUDA_VISIBLE_DEVICES is set to: {cuda_devices}")
        use_gpu = True
    else:
        print("CUDA_VISIBLE_DEVICES is not set. Using CPU.")
        use_gpu = False
    return use_gpu

def check_amd_gpu():
    hip_devices = os.environ.get("ROCR_VISIBLE_DEVICES", "")
    if hip_devices:
        print(f"ROCR_VISIBLE_DEVICES is set to: {hip_devices}")
        use_gpu = True
    else:
        print("ROCR_VISIBLE_DEVICES is not set. Using CPU.")
        use_gpu = False
    return use_gpu

# -------------------------------------------------------
# Get the number of GPUs visible.
# -------------------------------------------------------
def get_n_gpus():
    return torch.cuda.device_count()


# -------------------------------------------------------
# Get the number of GPUs visible.
# -------------------------------------------------------
def get_n_cpus():
    return psutil.cpu_count(logical=False) or psutil.cpu_count(logical=True)


# -------------------------------------------------------
# Function to choose the appropriate executor
# -------------------------------------------------------
def choose_executor(dev_type="cpu", max_workers=None):
    if dev_type == "cpu":
        #mp.set_start_method("fork", force=True) # faster on linux
        #ctx = mp.get_context("fork") # faster on linux due to copy-on-write
        mp.set_start_method("spawn", force=True) # safe with pytorch
        ctx = mp.get_context("spawn") # safe with pytorch
        # Choose ProcessPoolExecutor for CPU-bound tasks
        return ProcessPoolExecutor(mp_context=ctx, max_workers=max_workers)
    else:
        mp.set_start_method("spawn", force=True)
        # Choose ThreadPoolExecutor for GPU-bound tasks
        return ThreadPoolExecutor(max_workers=max_workers)


# -------------------------------------------------------
# Get a GPU that is not occupied
# -------------------------------------------------------
def get_dev(gpu_q: Queue = None) -> Tuple[str, int]:
    dev = "cpu"
    gpu_id = -1
    if gpu_q is not None:
        gpu_id = gpu_q.get()
        dev = f"cuda:{gpu_id}"
    return (dev, gpu_id)


# -------------------------------------------------------
# Return the list of colums that is not in `non_feat_cols`
# -------------------------------------------------------
def cols_except(data_df: pd.DataFrame,
                non_feat_cols: list[str] = ['machine']
)-> list[str]:
    feat_cols = [col for col in data_df.columns if col not in non_feat_cols]
    return feat_cols


# -------------------------------------------------------
# Return the number of NAs in the dataframe, and write out
# the coordinates of them
# -------------------------------------------------------
def locate_NAs(df: pd.DataFrame,
               where: str = "",
               show_T: bool = False,
               f: TextIO = None):
    num_NAs = df.isna().sum().sum()
    if num_NAs > 0:
        print(f"Number of NAs " + where + " : {num_NAs}", file=f)

        if show_T:
            for row, col in zip(*df.isna().to_numpy().nonzero()):
                print(f"""NaN at row={df.index[row]},
                          column={df.columns[col]},
                          T={df.iloc[row]['REALTIME (sec)']}""", file=f)
        else:
            for row, col in zip(*df.isna().to_numpy().nonzero()):
                print(f"""NaN at row={df.index[row]},
                          column={df.columns[col]}""", file=f)
    return num_NAs


# -------------------------------------------------------
# Write basic statistics on numeric features of a dataframe
# -------------------------------------------------------
def feature_stats(df: pd.DataFrame,
                  f: TextIO = None,
                  header: str = "feature stats"):
    silenced = False
    if f is None:
        silenced = True
        f = open(os.devnull, 'w')

    numeric_df = df.select_dtypes(include='number')
    stats = numeric_df.agg(['min', 'median', 'mean', 'std', 'max'])
    print(f"\n----- {header} ----", file=f)
    with pd.option_context('display.max_rows', None):
        print(stats.T, file=f)

    if silenced:
        f.close()


# -------------------------------------------------------
# Load the application (performance counter) data and
# the machine benchmarking data (RAJAPerf) from files.
# -------------------------------------------------------
def get_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    # ------------------------------------------
    # Load application performance counter data
    # ------------------------------------------
    data_df = pd.read_csv('app_data_hpc/ds_train_updated.csv')
    # TODO: Remove the following line added for debugging
    # data_df.iloc[data_df.index % 4 == 0]

    # Drop columns that will not be used
    data_df = data_df.drop(columns=['duration',
                                    'PM_MATH_FLOP_CMPL',
                                    'L1-DCACHE-LOAD-MISSES',
                                    'L1-ICACHE-LOAD-MISSES'])

    # Set sample id to keep track of which sample is used
    # (sid + 1) should match the line number in the data file
    data_df['sid'] = range(1, len(data_df) + 1)

    # Drop samples without the execution time measured or the identifier
    data_df = data_df.dropna(subset=['machine', 'app', 'args', 'ranks','REALTIME (sec)'])

    # Filter out samples that are not to be used
    data_df = data_df.loc[data_df['machine'] != 'corona']
    data_df = data_df.loc[data_df['app'] != 'sw4lite']

    # -1 was recorded to indicate that the performance
    # profiling tool did not report the particular metric
    # that is one of those in `cols_to_replace` below.
    # Here, replace '-1', which encodes N/A, with '0'
    cols_to_replace = ['L1_STM', 'L2_LDM', 'L2_STM', 'FP_SINGLE', 'FP_DOUBLE', 'ARITH']
    data_df[cols_to_replace].replace(-1, 0, inplace=True)
    data_df[APP_FEATURES] = data_df[APP_FEATURES].fillna(0.0)


    # -------------------------------------------------------
    # Load RAJAPerf data, i.e., machine characterization data
    # -------------------------------------------------------
    file = 'raja-data/machine_rep.txt'
    raja_df = pd.read_csv(file)
    raja_df.loc[raja_df['machine'] == 'ec2-c5n', 'machine'] = 'ec2-c5.metal'
    raja_df.loc[raja_df['machine'] == 'ec2-c6i', 'machine'] = 'ec2-c6i.metal'
    raja_df = raja_df.fillna(0.0)

    # Set the global variable of the list of feature columns in the machine sample
    global MACH_FEATURES
    MACH_FEATURES = list(raja_df.drop(columns=['machine']).columns)

    return (data_df, raja_df)


# -------------------------------------------------------
# Show basic statistics on feature values.
# -------------------------------------------------------
def show_feature_info(data_df: pd.DataFrame, f: TextIO = None):
    silenced = False
    if f is None:
        silenced = True
        f = open(os.devnull, 'w')

    temp_df = data_df.drop(columns=['machine','app','args','ranks','REALTIME (sec)'])
    num_rows, num_cols = temp_df.shape
    print(f"Number of samples: {num_rows}, Number of features: {num_cols}", file=f)
    print("Total number of -1: {}".format((temp_df == -1).sum().sum()), file=f)
    numeric_df = temp_df.select_dtypes(include='number')
    print("Total number of negatives: {}".format((numeric_df < 0).sum().sum()), file=f)
    print("Total number of 0: {}".format((temp_df == 0).sum().sum()), file=f)
    print("Total number of NA: {}".format(temp_df.isna().sum().sum()), file=f)
    non_numeric_mask = temp_df.applymap(lambda x: not pd.api.types.is_number(x))
    print("Total number of non-numeric: {}".format(non_numeric_mask.sum().sum()), file=f)
    del temp_df
    gc.collect()

    if silenced:
        f.close()


# -------------------------------------------------------
# Apply RobustScaler to colums identified by `feat_cols`.
# The basic statistics will be printed out to the file `f_feat`.
# If scaler, a pre-fit RobustScaler object, is given,
# it will transform the feature columns. Otherwise, a new
# one is created and fitted to the data.
# -------------------------------------------------------
def apply_RobustScaler(data_df: pd.DataFrame,
                       feat_cols: list[str] = APP_FEATURES,
                       scaler: RobustScaler = None,
                       f_feat: TextIO = None
) -> Tuple[pd.DataFrame, RobustScaler]:

    feat_df = data_df[feat_cols].select_dtypes(include='number')

    silenced = False
    if f_feat is None:
        silenced = True
        f_feat = open(os.devnull, 'w')

    if scaler is None:
        scaler = RobustScaler()
        X_scaler = scaler.fit_transform(feat_df)
    else:
        X_scaler = scaler.transform(feat_df)

    feat_df = pd.DataFrame(X_scaler,
                           columns = feat_df.columns,
                           index = feat_df.index)

    feature_stats(feat_df, f_feat,
                  "stats of features after applying RobustScaler")

    data_df[feat_cols] = feat_df

    if silenced:
        f_feat.close()

    return (data_df, scaler)


# -------------------------------------------------------
# Apply PowerTransformer to colums that are identified by
# `feat_cols`. The basic statistics will be printed
# out to the file `f_feat`.
# If scaler, a pre-fit PowerTransformer object, is given,
# it will transform the feature columns. Otherwise, a new
# one is created and fitted to the data.
# -------------------------------------------------------
def apply_PowerTransformer(data_df: pd.DataFrame,
                           feat_cols: list[str] = MACH_FEATURES,
                           scaler: PowerTransformer = None,
                           f_feat: TextIO = None
) -> Tuple[pd.DataFrame, PowerTransformer]:

    feat_df = data_df[feat_cols].select_dtypes(include='number')

    silenced = False
    if f_feat is None:
        silenced = True
        f_feat = open(os.devnull, 'w')

    if scaler is None:
        scaler = PowerTransformer()
        X_scaler = scaler.fit_transform(feat_df)
    else:
        X_scaler = scaler.transform(feat_df)

    feat_df = pd.DataFrame(X_scaler,
                           columns = feat_df.columns,
                           index = feat_df.index)

    feature_stats(feat_df, f_feat,
                  "stats of features after applying PowerTransformer")

    data_df[feat_cols] = feat_df

    if silenced:
        f_feat.close()

    return (data_df, scaler)


# -------------------------------------------------------
# Normalize the perf counter features by dividing them by
# the execution time. Then, apply RobustScaler.
# This returns the scaler object as well as the updated
# dataframe of the normalized data.
# If use_scaler is True but scaler is not given, a new
# scaler object will be fit to data. If a pre-fit scaler
# is given, it will be used only to transform.
# -------------------------------------------------------
def normalize(data_df: pd.DataFrame,
              feat_cols: list[str] = APP_FEATURES,
              f_feat: TextIO = None,
              use_scaler: bool = False,
              scaler: RobustScaler = None
) -> Tuple[pd.DataFrame, RobustScaler]:

    feat_df = data_df[feat_cols].select_dtypes(include='number')

    silenced = False
    if f_feat is None:
        silenced = True
        f_feat = open(os.devnull, 'w')

    feature_stats(feat_df, f_feat,
                  "stats of application features before normalization")

    # Divide counters by the execution time
    feat_df = feat_df.div(data_df['REALTIME (sec)'], axis=0)

    feature_stats(feat_df, f_feat,
                  "stats of application features after div_by_Texec")

    if use_scaler:
        feat_df, scaler = apply_RobustScaler(feat_df,
                                             APP_FEATURES,
                                             scaler,
                                             f_feat)

    data_df[feat_cols] = feat_df

    if silenced:
        f_feat.close()

    return (data_df, scaler)


# -------------------------------------------------------
# A wrapper to allow extracting latent embedding from
# PyTorch-TabNet 4.1.0
# -------------------------------------------------------
class TabNetPretrainerEmbedding(TabNetPretrainer):
    """
    Pooling modes for TabNet encoder embeddings:
        + mean:
          - Small datasets
          - Simple downstream models (LogReg, small MLPs, tree models)
          - Stable, smooth embeddings
          - When interpretability matters more than complexity
        + last:
          - the most refined representation
          - For lightweight downstream tasks, debugging, or analysis
          - Alternative to attention pooling without learning an
            extra vector and computing softmax
        + steps:
          - To feed embeddings into a sequential model (Transformers, RNNs, GRUs, LSTMs)
        + concat:
          - For maximum expressive power
          - For classical ML at downstream (XGBoost, CatBoost, LightGBM, logistic regression)
        + hybrid:
          - Compact but expressive embedding
          - Strong baseline for most datasets
          - Works with any downstream classifier
          - Best when steps encode complementary signals
        + attention:
          - To learn importance of each TabNet step
          - Dataset is large enough to learn attention parameters
          - When some steps capture more useful latent structure
          - When step importance changes across samples

    Usage:
        model = TabNetPretrainerEmbedding(...)
        emb = model.transform(X, mode="attention")
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.att_vector = None
        self.encoder_hook = None  # To store the hook reference
        self.steps_out = None

    def _hook_fn(self, module, input, output):
        """
        This hook captures the step outputs during the forward pass.
        """
        self.steps_out = output  # Save the output for later use

    def _ensure_att_vector(self):
        """Initialize attention vector if not already done."""
        if self.att_vector is None:
            if not hasattr(self, "network"):
                raise RuntimeError("Network not initialized. Call .fit() first.")
            net = self.network
            n_d = net.encoder.n_d
            device = next(net.parameters()).device
            self.att_vector = nn.Parameter(torch.randn(n_d, device=device))

    def fit(self, *args, **kwargs):
        """Override fit to register the hook after fitting."""
        super().fit(*args, **kwargs)
        if hasattr(self, 'network'):
            # Register hook after model is fitted and network is initialized
            self.encoder_hook = self.network.encoder.register_forward_hook(self._hook_fn)

    @torch.no_grad()
    def transform(self, X, mode="mean"):
        """
        Parameters
        ----------
        X : array-like or torch.Tensor
        mode : str, one of:
            "mean", "last", "steps", "concat", "hybrid", "attention"

        Returns
        -------
        Embedding ndarray of shape:
            mean: (B, n_d)
            last: (B, n_d)
            steps: (B, n_steps, n_d)
            concat: (B, n_steps*n_d)
            hybrid: (B, 3*n_d)
            attention: (B, n_d)
        """
        self._ensure_att_vector()
        net = self.network

        # Convert input to torch
        if isinstance(X, torch.Tensor):
            X_tensor = X.float()
        elif hasattr(X, "values"):  # pandas DataFrame/Series
            X_tensor = torch.tensor(X.values, dtype=torch.float32)
        else:
            X_tensor = torch.tensor(X, dtype=torch.float32)

        # Device match
        device = next(net.parameters()).device
        X_tensor = X_tensor.to(device)

        # Forward through the network (hook captures steps_out)
        _, embedded_x, _ = net(X_tensor)

        # Ensure steps_out was captured
        steps_out = getattr(self, 'steps_out', None)
        if steps_out is None:
            raise ValueError("Step outputs not captured. Ensure model is properly fitted.")

        # Extract decision embeddings for each step
        n_d = net.encoder.n_d
        H = torch.stack([s[:, :n_d] for s in steps_out[0]], dim=1)  # (B, T, n_d)
        B, T, n_d = H.shape

        # --- MODE ROUTING ---
        if mode == "mean":
            out = H.mean(dim=1)                           # (B, n_d)
        elif mode == "last":                              # (B, n_d)
            out = H[:, -1, :]
        elif mode == "steps":
            out = H                                       # (B, T, n_d)
        elif mode == "concat":
            out = H.reshape(B, T*n_d)                     # (B, T*n_d)
        elif mode == "hybrid":
            mean_pool = H.mean(dim=1)                     # (B, n_d)
            max_pool = H.max(dim=1)[0]                    # (B, n_d)
            last_step = H[:, -1, :]                       # (B, n_d)
            out = torch.cat([mean_pool, max_pool, last_step], dim=1)  # (B, 3*n_d)
        elif mode == "attention":
            # Score: tanh(H · w)
            scores = torch.tanh(H @ self.att_vector)      # (B, T)
            alpha = torch.softmax(scores, dim=1)          # (B, T)
            alpha = alpha.unsqueeze(-1)                   # (B, T, 1)
            out = torch.sum(alpha * H, dim=1)             # (B, n_d)
        else:
            raise ValueError(f"Invalid mode '{mode}'. Supported: "
                             "mean, last, steps, concat, hybrid, attention.")

        return out.cpu().numpy()


    @torch.no_grad()
    def get_attention_weights(self, X):
        """
        Returns raw attention scores and normalized weights for TabNet steps.

        Parameters
        ----------
        X : array-like or torch.Tensor

        Returns
        -------
        scores : np.ndarray, shape (B, T)
            Raw attention scores (before softmax)
        weights : np.ndarray, shape (B, T)
            Normalized attention weights (softmax)
        """
        self._ensure_att_vector()
        net = self.network

        # Convert input
        if isinstance(X, torch.Tensor):
            X_tensor = X.float()
        elif hasattr(X, "values"):  # pandas DataFrame
            X_tensor = torch.tensor(X.values, dtype=torch.float32)
        else:
            X_tensor = torch.tensor(X, dtype=torch.float32)

        # Device
        device = next(net.parameters()).device
        X_tensor = X_tensor.to(device)

        # Forward through the TabNet network (hook captures steps_out)
        _, embedded_x, _ = net(X_tensor)

        # Ensure steps_out was captured
        steps_out = getattr(self, 'steps_out', None)
        if steps_out is None:
            raise ValueError("Step outputs not captured. Ensure model is properly fitted.")

        n_d = net.encoder.n_d
        H = torch.stack([s[:, :n_d] for s in steps_out[0]], dim=1)  # (B, T, n_d)

        # Raw scores
        scores = torch.tanh(H @ self.att_vector)   # (B, T)

        # Normalized weights
        weights = torch.softmax(scores, dim=1)     # (B, T)

        return scores.cpu().numpy(), weights.cpu().numpy()

    @torch.no_grad()
    def plot_attention(self, X, idx=0, figsize=(6,4)):
        """
        Plot attention weights for sample idx in X.
        """
        import matplotlib.pyplot as plt

        scores, weights = self.get_attention_weights(X)

        score = scores[idx]
        weight = weights[idx]

        T = len(weight)

        plt.figure(figsize=figsize)
        plt.title(f"Attention Weights for Sample #{idx}")
        plt.plot(range(1, T+1), weight, marker='o', label="Attention Weight")
        plt.bar(range(1, T+1), weight, alpha=0.2)
        plt.ylabel("weight")
        plt.xlabel("TabNet Step")
        plt.xticks(range(1, T+1))
        plt.ylim(0, max(weight)*1.2)
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.savefig("tabnet.pdf", bbox_inches='tight') # PDF


    @torch.no_grad()
    def plot_attention_with_embedding(self, X, sample_indices=None):
        """
        Plots:
            1) Heatmap of step-wise attention weights
            2) Heatmap of weighted step embeddings (H*attention)
            3) Summary curves: mean, max, last-step attention

        Parameters
        ----------
        X : array-like or torch.Tensor
        sample_indices : list of int, optional
            Indices of samples to show in heatmap (default: first 20 samples)
        """
        self._ensure_att_vector()
        net = self.network

        # Convert input
        if isinstance(X, torch.Tensor):
            X_tensor = X.float()
        elif hasattr(X, "values"):  # pandas DataFrame
            X_tensor = torch.tensor(X.values, dtype=torch.float32)
        else:
            X_tensor = torch.tensor(X, dtype=torch.float32)

        device = next(net.parameters()).device
        X_tensor = X_tensor.to(device)

        # Forward through the network (hook captures steps_out)
        _, embedded_x, _ = net(X_tensor)

        # Ensure steps_out was captured
        steps_out = getattr(self, 'steps_out', None)
        if steps_out is None:
            raise ValueError("Step outputs not captured. Ensure model is properly fitted.")

        n_d = net.encoder.n_d
        H = torch.stack([s[:, :n_d] for s in steps_out[0]], dim=1)  # (B, T, n_d)

        # Attention weights (softmax applied)
        scores = torch.tanh(H @ self.att_vector)   # (B, T)
        alphas = torch.softmax(scores, dim=1)      # (B, T)

        B, T, n_d = H.shape

        if sample_indices is None:
            sample_indices = list(range(min(20, B)))  # default first 20

        # Weighted embeddings: multiply H by attention weights per step
        weighted_H = H * alphas.unsqueeze(-1)      # (B, T, n_d)

        # --- Plotting ---
        fig, axes = plt.subplots(2, 1, figsize=(T * 0.5 + 3, len(sample_indices) * 0.5 + 6))

        # 1) Attention heatmap
        sns.heatmap(alphas[sample_indices].detach().cpu().numpy(), annot=True, fmt=".2f", cmap="viridis",
                    yticklabels=sample_indices, ax=axes[0])
        axes[0].set_xlabel("Decision Step")
        axes[0].set_ylabel("Sample Index")
        axes[0].set_title("Step-wise Attention Heatmap")

        # Summary curves
        mean_alpha = alphas.mean(axis=0).detach().cpu().numpy()
        max_alpha = alphas.max(axis=0).values.detach().cpu().numpy()
        last_sample_alpha = alphas[sample_indices[-1], :].detach().cpu().numpy()
        ax2 = axes[0].twinx()
        ax2.plot(np.arange(0.5, T + 0.5, 1.0), mean_alpha, 'r-o', label="Mean")
        ax2.plot(np.arange(0.5, T + 0.5, 1.0), max_alpha, 'g--s', label="Max")
        ax2.plot(np.arange(0.5, T + 0.5, 1.0), last_sample_alpha, 'b-^', label="Last sample")
        ax2.set_ylabel("Summary attention")
        ax2.legend(loc='upper right')

        # 2) Weighted embedding heatmap
        # Collapse n_d dimension using mean (or could use other pooling)
        emb_summary = weighted_H[sample_indices].mean(axis=2).cpu().detach().numpy()  # (len(samples), T)
        sns.heatmap(emb_summary, annot=False, cmap="coolwarm", yticklabels=sample_indices, ax=axes[1])
        axes[1].set_xlabel("Decision Step")
        axes[1].set_ylabel("Sample Index")
        axes[1].set_title("Weighted Step Embedding Heatmap (mean over n_d)")

        plt.tight_layout()
        plt.savefig("tabnet-heatmap.pdf", bbox_inches='tight') # PDF


# -------------------------------------------------------
# Apply TabNet-based unsupervised encoding to samples.
# Assume that data_df has already been normalized.
# -------------------------------------------------------
def use_tabnet(data_df: pd.DataFrame,
                  feat_cols: list[str] = APP_FEATURES,
                  pretrainer: TabNetPretrainer = None,
                  gpu_q: Queue = None,
                  plot_umap: bool = False,
                  plot_tSNE: bool = False,
                  f_feat: TextIO = None
) -> Tuple[pd.DataFrame, TabNetPretrainer]:

    silenced = False
    if f_feat is None:
        silenced = True
        f_feat = open(os.devnull, 'w')

    # Apply only to the feature columns
    feature_df = data_df[feat_cols]
    #print(feature_df.dtypes)
    X_float = feature_df.values.astype(np.float64)

    '''
    numeric_cols = feature_df.select_dtypes(include='number').columns
    non_numeric_cols = feature_df.select_dtypes(exclude='number').columns

    print("Numeric columns:", numeric_cols.tolist(), file=f_feat)
    print("Non-numeric columns:", non_numeric_cols.tolist(), file=f_feat)
    '''

    embeddings: np.array = None
    dev, gpu_id = get_dev(gpu_q)

    try:
        if pretrainer is None:
            pretrainer = TabNetPretrainerEmbedding(input_dim = feature_df.shape[1],
                                          n_d=32,
                                          n_a=32,
                                          n_steps=3,
                                          device_name = dev)
            # Pretrain TabNet in unsupervised mode
            pretrainer.fit(X_train=X_float,
                           max_epochs=200,
                           patience=20,
                           batch_size=TABNET_BATCH_SIZE,
                           virtual_batch_size=TABNET_BATCH_SIZE/2)
        # Extract embeddings
        embeddings = pretrainer.transform(X_float, "last")
    except Exception as e:
        print("Failed to create and fit TabNetPretrainer:", e)
        if gpu_q is not None:
            torch.cuda.synchronize()
            torch.cuda.empty_cache()
        raise
    finally:
        if gpu_q is not None:
            gpu_q.put(gpu_id)

    embed_df = pd.DataFrame(
        embeddings,
        index=data_df.index,
        columns=[f"a_emb_{i}" for i in range(embeddings.shape[1])]
    )
    feature_stats(embed_df, f_feat,
                  "stats of application features after TabNet embedding")
    del X_float, embeddings

    if plot_umap or plot_tSNE:
        X = embed_df.select_dtypes(include='number')
        X_scaled = StandardScaler().fit_transform(X)

    if plot_umap:
        X_umap = umap.UMAP(random_state=1119).fit_transform(X_scaled)
        labels = OPTICS(min_samples=5, xi=0.05).fit_predict(X_umap)
        sns.scatterplot(x=X_umap[:,0], y=X_umap[:,1], hue=labels, palette='tab10')
        plt.title("UMAP Clusters of performance counter embeddings")
        plt.savefig("UMAP_app.pdf", bbox_inches='tight') # PDF

    if plot_tSNE:
        X_tsne = TSNE(n_components=2).fit_transform(X_scaled)
        labels = OPTICS(min_samples=5, xi=0.05).fit_predict(X_tsne)
        sns.scatterplot(x=X_umap[:,0], y=X_umap[:,1], hue=labels, palette='tab10')
        plt.title("tSNE Clusters of performance counter embeddings")
        plt.savefig("tSNE_app.pdf", bbox_inches='tight') # PDF

    non_feat_cols = [col for col in data_df.columns if col not in feat_cols]
    data_df = pd.concat([data_df[non_feat_cols], embed_df], axis=1)

    if silenced:
        f_feat.close()

    return (data_df, pretrainer)


# -------------------------------------------------------
# Apply series of feature transformations to a training
# set and a test/validation set.
# -------------------------------------------------------
def feat_transform(X_train_raw: pd.DataFrame,
                   X_test_raw: pd.DataFrame = None,
                   app_feats: list[str] = APP_FEATURES,
                   mach_feats: list[str] = MACH_COMB_FEATS,
                   gpu_q: Queue = None,
                   plot_umap: bool = False,
                   plot_tSNE: bool = False,
                   f_feat: TextIO = None,
                   scaler_app: RobustScaler = None,
                   scaler_mach: PowerTransformer = None,
                   pretrainer: TabNetPretrainer = None
) -> Tuple[pd.DataFrame, pd.DataFrame, RobustScaler, PowerTransformer, TabNetPretrainer]:

    # Additional normalization regarding feature distribution.
    # Apply RobustScaler to application features where there are
    # many outliers.  Apply PowerTransformer to machine features.
    X_train, scaler_app = apply_RobustScaler(X_train_raw,
                                             app_feats,
                                             scaler_app,
                                             f_feat)
    X_train, scaler_mach = apply_PowerTransformer(X_train,
                                                  mach_feats,
                                                  scaler_mach,
                                                  f_feat)
    # TabNet unsupervised embedding of the training set
    X_train, pretrainer = use_tabnet(X_train,
                                        app_feats + mach_feats,
                                        pretrainer,
                                        gpu_q, plot_umap, plot_tSNE, f_feat)

    if X_test_raw is not None:
        # Apply the scaler tuned with the training set to the validation set
        X_test, _ = apply_RobustScaler(X_test_raw,
                                       app_feats,
                                       scaler_app,
                                       f_feat)
        X_test, _ = apply_PowerTransformer(X_test,
                                           mach_feats,
                                           scaler_mach,
                                           f_feat)

        if f_feat is not None:
            pretrainer.plot_attention(X_test, idx=0)
            scores, weights = pretrainer.get_attention_weights(X_test)
            print("Scores:", scores[0], file=f_feat)
            print("Weights:", weights[0], file=f_feat)
            pretrainer.plot_attention_with_embedding(
                X_test, list(range(10,50))
            )
        # Apply the encoder tuned with the training set to the validation set
        X_test, _ = use_tabnet(X_test,
                                      app_feats + mach_feats,
                                      pretrainer,
                                      gpu_q, plot_umap, plot_tSNE, f_feat)

    # TODO: option to switch to dimensionality reduction in place of tabnet

    return (X_train, X_test, scaler_app, scaler_mach, pretrainer)


# -------------------------------------------------------
# Show the basic statistics on samples and the first two
# samples as examples.
# -------------------------------------------------------
def show_data_summary(data_df: pd.DataFrame,
                      machine_col='machine',
                      f_feat: TextIO = None):
    silenced = False
    if f_feat is None:
        silenced = True
        f_feat = open(os.devnull, 'w')

    apps = data_df['app'].unique()
    machines = data_df[machine_col].unique()
    label_num_samples_per_mach = []
    num_samples_per_mach = []

    df_rows, df_cols = data_df.shape
    print('Num samples = ', df_rows, file=f_feat)
    print('Num columns = ', df_cols, file=f_feat)
    print('\n---------------------------------------------', file=f_feat)
    print('Num apps = ', len(apps), file=f_feat)
    for app in apps:
        print('    - ', app, len(data_df[data_df['app'] == app]), file=f_feat)
    print('\n---------------------------------------------', file=f_feat)
    print('Num machines = ', len(machines), file=f_feat)
    for machine in machines:
        num_msamples = len(data_df[data_df[machine_col] == machine])
        label_num_samples_per_mach.append(machine)
        num_samples_per_mach.append(num_msamples)
        print('    - ', machine, num_msamples, file=f_feat)
    print('---------------------------------------------', file=f_feat)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.width', 0)
    print('\n---------------------sample 1------------------\n',
          data_df.iloc[0,:], file=f_feat)
    print('\n---------------------sample 2------------------\n',
          data_df.iloc[1,:], file=f_feat)

    if silenced:
        f_feat.close()

    return (label_num_samples_per_mach, num_samples_per_mach)


# -------------------------------------------------------
# The relative performance is calcualated from the samples
# collected by running the same app with the same args
# using the same ranks on two platforms that can be
# different or the same. If they are the same, then the
# relative performance would be 1. This function would
# only keep runs that run on at least two different platforms,
# i.e., the same app, args, and rank but different systems.
# One GPU is considered one rank.
# If this function is not called, the runs with only
# self-machting cases will be added to training samples,
# which might still be useful.
# -------------------------------------------------------
def drop_unmatched_rows(data_df: pd.DataFrame) -> pd.DataFrame:
    all_machines = data_df['machine'].unique()
    num_no_match = 0
    no_match_rows = []
    for index, row in data_df.iterrows():
        row_args = row['args']
        row_ranks = row['ranks']
        # assert that this run is available in all machines
        row_is_common = False
        comp_row = data_df.loc[data_df['args'] == row_args].loc[data_df['ranks'] == row_ranks]
        if len(comp_row) < 2:
            num_no_match += 1
            no_match_rows.append(index)
    # drop the rows with no matches
    return data_df.drop(index=no_match_rows)


# -------------------------------------------------------
# For each specific choice of app, args and ranks, we want to
# make combinations of base machine and target machine available.
# We know that for N machines, there are N*N=N^2 combinations,
# including the self pairing with relative performance 1.0.
# For each combination, we will later calculate the relative
# performance, and here we only do pairing.
# -------------------------------------------------------
def create_machine_combinations(data_df: pd.DataFrame) -> pd.DataFrame:
    # This renaming is to prepare source and target machine combinations
    data_df = data_df.rename(columns={'machine': 'source machine'})

    new_data_df: pd.DataFrame = None
    all_args = data_df.args.unique()
    for args in all_args:
        filtered_by_args = data_df[data_df.args == args]
        all_ranks = filtered_by_args.ranks.unique()
        for ranks in all_ranks:
            filtered_by_ranks_and_args = filtered_by_args[filtered_by_args.ranks == ranks]
            all_machines = filtered_by_ranks_and_args['source machine'].unique()
            for source_machine in all_machines:
                # print('num all machines', len(all_machines))
                temp_df = filtered_by_ranks_and_args[filtered_by_ranks_and_args['source machine']
                                                     == source_machine].copy(deep=True)
                base_df = temp_df.copy(deep=True)
                # replicating the perf counter features of the source machine
                # as many as the number of target machines.
                # we don't need the perf counter features of the target machine.
                # We make placeholder lines for machine characterization features.
                for i in range (1, len(all_machines)):
                    temp_df = pd.concat([temp_df, base_df.copy(deep=True)])
                temp_df['target machine'] = all_machines.copy()
                new_data_df = pd.concat([new_data_df, temp_df])

    return new_data_df


# -------------------------------------------------------
# Concatenate each sample created via create_machine_combinations()
# with the machine representation samples corresponding to
# the source machine and the target machine.
# -------------------------------------------------------
def merge_benchmarks(data_df: pd.DataFrame,
                     raja_df: pd.DataFrame,
                     f_feat: TextIO = None,
                     use_scaler: bool = False,
                     scaler: PowerTransformer = None
) -> Tuple[pd.DataFrame, PowerTransformer]:

    silenced = False
    if f_feat is None:
        silenced = True
        f_feat = open(os.devnull, 'w')

    # Hide the machine name column and leave only the feature columns
    feature_df = raja_df.drop(columns=['machine'])

    if use_scaler:
        feature_stats(feature_df, f_feat,
                      "stats of machine features before PowerTransformer")
        if scaler == None:
            scaler = PowerTransformer()
            X_scaler = scaler.fit_transform(feature_df)
        else:
            X_scaler = scaler.transform(feature_df)

        feature_df = pd.DataFrame(X_scaler,
                                  columns = feature_df.columns,
                                  index = feature_df.index)
        method = " with PowerTransformer"
    else:
        method = ""

    feature_stats(feature_df, f_feat,
                  "stats of machine features" + method)

    raja_df[feature_df.columns] = feature_df

    arch_source = raja_df.add_prefix('source ')
    arch_target = raja_df.add_prefix('target ')

    global MACH_COMB_FEATS
    MACH_COMB_FEATS = list(arch_source.columns)[1:] + list(arch_target.columns)[1:]

    data_df = data_df.merge(arch_source, on=['source machine'])
    data_df = data_df.merge(arch_target, on=['target machine'])

    del raja_df, arch_source, arch_target
    gc.collect()

    if silenced:
        f_feat.close()

    return (data_df, scaler)


# -------------------------------------------------------
# Compute relative performance T_source/T_target
# -------------------------------------------------------
def calc_relative_performances(data_df: pd.DataFrame) -> pd.DataFrame:
    rel_perf_list = []
    target_sid = []
    #with open('source_target_speedup.txt', 'w') as f:
    for index, row in data_df.iterrows():
        # print(row)
        base_performance = row['REALTIME (sec)']
        row_args = row['args']
        row_ranks = row['ranks']
        source_machine = row['source machine']
        target_machine = row['target machine']

        comp_row = data_df[(data_df['args'] == row_args) \
                 & (data_df['source machine'] == target_machine) \
                 & (data_df['target machine'] == source_machine) \
                 & (data_df['ranks'] == row_ranks)]

        target_performance = comp_row['REALTIME (sec)'].iloc[0]
        relative_performance = base_performance/target_performance
        #relative_performance = target_performance/base_performance
        rel_perf_list.append(relative_performance)
        target_sid.append(comp_row['sid'].iloc[0])

    data_df['relative performance'] = rel_perf_list
    data_df['target_sid'] = target_sid;

    '''
    # Sanity check of relative performance by calculating
    # source/target * target/source = 1
    import math
    with open('source_target_speedup.txt', 'w') as f:
        for index, row in data_df.iterrows():
          row_args = row['args']
          row_ranks = row['ranks']
          source_machine = row['source machine']
          target_machine = row['target machine']

          comp_row = data_df[(data_df['args'] == row_args) \
                & (data_df['source machine'] == target_machine) \
                & (data_df['target machine'] == source_machine) \
                & (data_df['ranks'] == row_ranks)]

          if not math.isclose(row['relative performance'] *
                              comp_row['relative performance'], 1.0, rel_tol=1e-9) :
              print(f"{source_machine}, {target_machine}, \
                      {row['sid']}, {comp_row['sid']}, \
                      {row['relative_performance']}, \
                      {comp_row['relative performance']}", \
                      file = f)
    '''
    return data_df


# -------------------------------------------------------
# Write the basic statistics on the relative performance
# for each pair of source and target machines into files.
# -------------------------------------------------------
def write_relative_perf_stats(data_df: pd.DataFrame):
    from collections import defaultdict
    raw_dict = defaultdict(list)
    sum_dict = defaultdict(lambda: [0.0, 0])
    max_dict = defaultdict(lambda: float('-inf'))
    min_dict = defaultdict(lambda: float('inf'))

    with open('rperf_raw.txt', 'w') as f:
        print("#rel_perf,\tm_src,\tm_tgt,\tapp,\targs,\tsid_src,\tsid_tgt", file=f)
        for index, row in data_df.iterrows():
            m_s = row['source machine']
            m_t = row['target machine']
            # speedup
            rel = row['relative performance']
            cur = sum_dict[(m_s, m_t)];
            # Keep track of the sum of relative perf and the number of records
            sum_dict[(m_s, m_t)] = (cur[0]+rel, cur[1]+1)

            cur_min = min_dict[(m_s, m_t)]
            if (cur_min > rel) :
                min_dict[(m_s, m_t)] = rel;

            cur_max = max_dict[(m_s, m_t)]
            if (cur_max < rel) :
                max_dict[(m_s, m_t)] = rel;

            raw_dict[(m_s, m_t)].append(rel)
            print('%.3f,\t%s,\t%s,\t%s,\t\"%s\",\t%u,\t%u' %
                  (rel, m_s, m_t, row['app'], row['args'],
                  row['sid'], row['target_sid'] ), file=f)

    with open('rperf_min.txt', 'w') as f:
        print("#rel_perf,\tm_src,\tm_tgt", file=f)
        for (m_s, m_t), rel in min_dict.items():
            print(f"{rel},\t{m_s},\t{m_t}", file=f)

    with open('rperf_max.txt', 'w') as f:
        print("#rel_perf,\tm_src,\tm_tgt", file=f)
        for (m_s, m_t), rel in max_dict.items():
            print(f"{rel},\t{m_s},\t{m_t}", file=f)

    with open('rperf_avg.txt', 'w') as f:
        print("#rel_perf,\tcnt,\tm_src,\tm_tgt", file=f)
        for (m_s, m_t), rel in sum_dict.items():
            print(f"{rel[0]/rel[1]},\t{rel[1]},\t{m_s},\t{m_t}", file=f)

    with open('rperf_raw.txt', 'w') as f:
        print("#rel_perf,\tm_src,\tm_tgt", file=f)
        for (m_s, m_t), rel in raw_dict.items():
            print(f"{rel},\t{m_s},\t{m_t}", file=f)


# -------------------------------------------------------
# Remove the columns that were used to match records
# and to keep track as they are not used during training.
# -------------------------------------------------------
def remove_unneeded_columns(data_df: pd.DataFrame) -> pd.DataFrame:
    to_rm = ['source machine', 'app', 'args', 'ranks', 'REALTIME (sec)',
             'sid', 'target machine', 'target_sid']
    refined_df = data_df.drop(columns=to_rm)
    return refined_df


# -------------------------------------------------------
# Split sample table into feature and labeli.
# The label is in the 'relative performance' column.
# -------------------------------------------------------
def split_x_y(refined_df: pd.DataFrame) -> (np.ndarray, np.ndarray):
    run_data = refined_df.drop(columns='relative performance').to_numpy()
    relative_performance_values = refined_df['relative performance'].to_numpy()
    return (run_data, relative_performance_values)

def split_x_y_df(refined_df: pd.DataFrame) -> (pd.DataFrame, pd.DataFrame):
    run_data = refined_df.drop(columns='relative performance')
    relative_performance_values = refined_df['relative performance']
    return (run_data, relative_performance_values)


# -------------------------------------------------------
# This performs the whole data preparation from reading
# input files to constructing sample table
# If get_sample_id is True, this function also returns the
# list of tuples ['sid', 'source machine', 'target machine']
# for all the samples. This will allow feature transformation
# per cross-validation data fold.
# -------------------------------------------------------
def prepare_data(f_feat: TextIO = None,
                 get_sample_id: bool = False
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:

    silenced = False
    if f_feat is None:
        silenced = True
        f_feat = open(os.devnull, 'w')

    data_df, raja_df = get_data()

    show_feature_info(data_df, f_feat)

    # Only apply div_by_Texec, but not RobustScaler at this point
    data_df, _ = normalize(data_df, APP_FEATURES, f_feat, False)
    locate_NAs(data_df, "after normalize", True, f_feat)

    #data_df = drop_unmatched_rows(data_df)

    # If there exist N samples of a specific app+args+rank combination collected
    # from N machines, the sample from each source machine is replicated to N
    # target machines including itself. The new sample includes an extra column
    # 'target machine'.
    # Consequently, total NxN samples are created out of the original N samples.
    data_df = create_machine_combinations(data_df)

    # Merge machine representation data with application perf counter data
    data_df, mach_scaler = merge_benchmarks(data_df, raja_df, f_feat)
    del raja_df
    gc.collect()

    data_df = calc_relative_performances(data_df)
    write_relative_perf_stats(data_df)

    sid_df: pd.DataFrame = None
    if get_sample_id:
        sid_df = data_df[['sid', 'source machine', 'target machine']]

    refined_df = remove_unneeded_columns(data_df)

    # Information about data
    show_data_summary(data_df, 'source machine', f_feat)
    data_df._clear_item_cache()

    X, y = split_x_y_df(refined_df)

    print(f"\nFinal features ({X.shape[1]}):", file=f_feat)
    print(list(X.columns), file=f_feat)

    if silenced:
        f_feat.close()

    return (X, y, sid_df)


# -------------------------------------------------------
# MAPE metric. This is for final reporting
# -------------------------------------------------------
def safe_mape(y_true, y_pred, eps=1e-7):
    return np.mean(np.abs((y_true - y_pred) / np.maximum(np.abs(y_true), eps))) * 100


# -------------------------------------------------------
# This is eval_metric that can be used for cross
# validation and early termination
# -------------------------------------------------------
def smape_eval(preds: np.ndarray, dtrain: xgb.DMatrix):
    y_true = dtrain.get_label()
    denom = (np.abs(y_true) + np.abs(preds)) / 2.0
    # avoid division by zero
    denom = np.where(denom == 0, 1e-7, denom)
    smape = np.mean(np.abs(preds - y_true) / denom) * 100.0
    return ('smape', smape)
    #return ('smape', smape, False)

def eval_setup(use_smape: bool):
    if use_smape:
        #feval = smape_eval
        #maximize = False  # lower is better with SMAPE
        #eval_metric = None  # don't set default metric
        eval_metric = 'mae'  # don't set default metric
    else:
        #feval = None
        #maximize = None # With XGBoost 3.1.1 this is passed to callback
        eval_metric = "logloss" # or "mae", "rmse"
        #eval_metric = "mae" # "logloss" or "rmse"
        #eval_metric = "rmse" # "mae" or "logloss"
    #return feval, maximize, eval_metric


# -------------------------------------------------------
# Optuna objective function
# -------------------------------------------------------
def objective_factory(kfold_rounds: List[List[Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]]],
                      gpu_q: Queue = None):
    #n_gpus = get_n_gpus()

    if gpu_q is None:
        use_gpu = False
    else:
        use_gpu = True

    def objective(trial):
        # Unique RNG seed based on both the process id and the trial number
        cv_seed = os.getpid() * 16384 + trial.number * 17 + 7
        rng = np.random.default_rng(cv_seed)
        # Pick a k-fold set randomly
        n_preset_kfolds = len(kfold_rounds)
        folds = kfold_rounds[rng.integers(0, n_preset_kfolds)]
        # Compute stdev on label so that it can define the range of huber slope
        # hyper parameter search
        _,_, y_train, y_valid = folds[0]
        label_std = pd.concat([y_train, y_valid], ignore_index=True).std()

        params_seed = trial.suggest_int("seed", 0, 2**31 - 1)

        dev, gpu_id = get_dev(gpu_q)
        #gpu_id  = trial.number % n_gpus

        try:
            # ------------------------
            # Hyperparameter search space
            # ------------------------
            #feval, maximize, eval_metric = eval_setup(use_smape)

            params = {
                "objective": "reg:pseudohubererror",
                #"eval_metric": eval_metric,
                "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.2, log=True),
                "max_depth": trial.suggest_int("max_depth", 3, 12),
                "subsample": trial.suggest_float("subsample", 0.7, 1.0),
                "colsample_bytree": trial.suggest_float("colsample_bytree", 0.7, 1.0),
                "huber_slope": trial.suggest_float(
                    "huber_slope",
                    0.01 * label_std,
                    10.0 * label_std,
                    log=True,
                ),
                "tree_method": "auto" if use_gpu else "hist",
                #"predictor": "gpu_predictor" if use_gpu else "cpu_predictor",
                "device": dev,
                "n_jobs": 1,
                "seed": params_seed
            }

            n_estimators = trial.suggest_int("n_estimators", 300, 2000)

            # -----------------------------------
            # 5-fold cross-validation
            # -----------------------------------
            mape_scores = []

            for fold_num, (X_train, X_valid, y_train, y_valid) in enumerate(folds, 0):

                # Create DMatrices for XGBoost
                dtrain = xgb.DMatrix(data=X_train, label=y_train)
                dvalid = xgb.DMatrix(data=X_valid, label=y_valid)

                # Specifying a validation set for early stopping
                evals = [(dvalid, "validation")]

                # Train model with early stopping
                model = xgb.train(
                    params=params,
                    dtrain=dtrain,
                    num_boost_round=n_estimators,
                    evals=evals,
                    #feval=feval, # no longer supported in XGBoost 3.1.1
                    #maximize=maximize, # lower is better with SMAPE
                    #early_stopping_rounds=50, # no longer supported in XGBoost 3.1.1
                    callbacks=[xgb.callback.EarlyStopping(rounds=50, save_best=True, maximize=False)], # This is the XGBoost 3.1.1 way
                    verbose_eval=False
                )

                # Predictions
                y_pred = model.predict(dvalid)
                mape_scores.append(safe_mape(y_valid, y_pred))

                # Optuna pruning
                trial.report(np.mean(mape_scores), len(mape_scores))
                if trial.should_prune():
                    raise optuna.exceptions.TrialPruned()
        except Exception as e:
            print(f"[Exception] on {dev}: {e}")
            if use_gpu:
                torch.cuda.synchronize()
                torch.cuda.empty_cache()
            raise
        finally:
            if use_gpu:
                gpu_q.put(gpu_id)

        return np.mean(mape_scores)
    return objective


# -------------------------------------------------------
# Plot actual label vs predicted
# -------------------------------------------------------
def plot_prediction(y_true, y_pred):
    plt.figure(figsize=(8, 8))
    plt.scatter(y_true, y_pred, alpha=0.6, color='blue', edgecolor='k')
    plt.plot([y_true.min(), y_true.max()],
             [y_true.min(), y_true.max()],
             color='red', linestyle='--', linewidth=2)  # perfect prediction line
    plt.xlabel("Actual Labels")
    plt.ylabel("Predicted Labels")
    plt.title("Predicted vs Actual Labels")
    plt.grid(True, which='both', linestyle='--', linewidth=0.7)
    #plt.savefig("pred_vs_actual.png", dpi=300, bbox_inches='tight') # PNG
    plt.savefig("pred_vs_actual.pdf", bbox_inches='tight')          # PDF
    plt.show()


# -------------------------------------------------------
# Pre-generate K-fold indices for multiple (N_PRESET_KFOLDS)
# cross-validation rounds
# -------------------------------------------------------
def make_KFold_rounds(X: pd.DataFrame,
                      y: pd.DataFrame,
                      gpu_q: Queue = None
) -> List[List[Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]]]:

    t_start = time.time()

    kf = KFold(n_splits=N_FOLDS, shuffle=True, random_state=42)

    kfold_rounds = []

    # ---------------------------------------------------------
    # Generate flattened task list (all rounds × all folds)
    # --------------------------------------------------------
    tasks: List[Tuple] = []

    # Generate and store multiple K-fold splits
    for i_round in range(N_PRESET_KFOLDS):
        folds = []
        for k, (train_idx, valid_idx) in enumerate(kf.split(X)):
            X_train = X.iloc[train_idx]
            X_valid = X.iloc[valid_idx]
            y_train = y.iloc[train_idx]
            y_valid = y.iloc[valid_idx]
            tasks.append((i_round, k, X_train, X_valid, y_train, y_valid))

    # ---------------------------------------------------------
    # Pre-initialize nested result list
    # ---------------------------------------------------------
    kfold_rounds: List[List[Tuple]] = [
        [None] * N_FOLDS for _ in range(N_PRESET_KFOLDS)
    ]

    # ---------------------------------------------------------
    # Parallel execution
    # ---------------------------------------------------------
    if gpu_q is None:
        n_procs = get_n_cpus()
        dev="cpu"
    else:
        n_procs = get_n_gpus()
        dev="gpu"

    max_workers = min(len(tasks), 2 * n_procs)  # heuristic
    with choose_executor(dev, max_workers) as executor:
        futures = {}
        for t in tasks:
            i_round, k, X_train, X_valid, y_train, y_valid = t
            f = executor.submit(feat_transform, X_train, X_valid,
                                                APP_FEATURES,
                                                MACH_COMB_FEATS,
                                                gpu_q)
            futures[f] = (i_round, k, y_train, y_valid)

        # collect results
        for f in as_completed(futures):
            X_train_emb, X_valid_emb, _,_,_ = f.result()
            i_round, k, y_train, y_valid = futures[f]
            kfold_rounds[i_round][k] = (X_train_emb,
                                        X_valid_emb,
                                        y_train,
                                        y_valid)

    t_end = time.time()
    print(f"Elapsed time (make_KFold_rounds): {t_end - t_start:.4f} seconds")
    '''
    for i_round, folds in enumerate(kfold_rounds, 0):
        print(f"Round {i_round}:")
        for fold_num, (X_train, X_valid, y_train, y_valid) in enumerate(folds, 0):
            print(f"  Fold {fold_num}: {X_train.shape}, {X_valid.shape}, {y_train.shape}, {y_valid.shape}")
            print(f"                 : {X_train.stack().agg(['mean', 'std']:.4f).to_dict()},"
                                    f" {X_valid.stack().agg(['mean', 'std']:.4f).to_dict()},"
                                    f" {y_train.agg(['mean', 'std']:.4f).to_dict()},"
                                    f" {y_valid.agg(['mean', 'std']:.4f).to_dict()}")
    '''
    return kfold_rounds


# -------------------------------------------------------
# Main function
# -------------------------------------------------------
def main():
    print(f"XGBoost version: {xgb.__version__}")

    # Initialize GPU availability queue
    use_gpu = check_gpu()
    gpu_q = Queue() if use_gpu else None
    n_gpus = get_n_gpus()
    for gpu_id in range(n_gpus):
        gpu_q.put(gpu_id)

    plot_umap = True
    plot_tSNE = True
    use_smape = True

    # Open the file to write feature statistics
    fd = os.open("feature_stats.txt", os.O_WRONLY | os.O_CREAT | os.O_TRUNC)
    f_feat = os.fdopen(fd, "w")
    #f_feat = sys.stdout

    # Prepare training data, i.e., load application and machine data.
    # Then, join them and compute the label (relative performance)
    X, y, _ = prepare_data(f_feat)

    # Split data into a train set and a test set for final training.
    # Before final training, run hyper-paramter search by Optuna using
    # the train set.
    X_train_all_raw, X_test_raw, y_train_all, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Prepare data for k-fold rounds. Apply feature transforms.
    kfold_rounds = make_KFold_rounds(X_train_all_raw, y_train_all, gpu_q)

    print("Data ready!")

    # -------------------------------------------------------
    # Run Optuna for hyper-parameter tuning
    # -------------------------------------------------------

    objective = objective_factory(kfold_rounds, gpu_q)
    study = optuna.create_study(direction="minimize")
    study.optimize(objective,
                   n_trials=N_OPTUNA_TRIALS,
                   show_progress_bar=False,
                   n_jobs = get_n_gpus() if use_gpu else 20)

    print("\nBest parameters:")
    print(study.best_params)

    print("\nBest value (MAPE):")
    print(study.best_value)

    # -------------------------------------------------------
    # Transform data for training a final model. This transform
    # will not be the same as that performed during the Optuna
    # hyper-parameter search. We use the
    # However, there is no easy way to store the transformation
    # fitters of the best run. Regardless, the hyper-parameters
    # are to influence learning dynamics not to represent the
    # data, and should be general if CV was successful.
    # Note that we did not leak the information on data
    # into CV by not transforming the whole training set before
    # the hyper-parameter search.
    # Here, we fit transformation models to the full training set.
    # Then, apply the same transformation to the test set.
    # -------------------------------------------------------

    X_train_all, X_test, scaler_app, scaler_mach, pretrainer = \
        feat_transform(X_train_all_raw,
                       X_test_raw,
                       APP_FEATURES,
                       MACH_COMB_FEATS,
                       gpu_q,
                       plot_umap,
                       plot_tSNE,
                       f_feat)
    f_feat.close() # close the feature statistics output file

    # -------------------------------------------------------
    # Train final model on full dataset
    # -------------------------------------------------------
    # Split train data for early stopping
    X_train, X_es, y_train, y_es = train_test_split(
        X_train_all, y_train_all, test_size=0.1, random_state=42
    )

    #feval, maximize, eval_metric = eval_setup(use_smape)
    best_params = study.best_params
    best_params.update({
        "objective": "reg:pseudohubererror",
        #"eval_metric": eval_metric,
        "tree_method": "auto" if use_gpu else "hist",
        #"predictor": "gpu_predictor" if use_gpu else "cpu_predictor",
        "device": "cuda:0" if use_gpu else "cpu",
        "seed": 42
    })
    n_estimators = best_params.pop("n_estimators")


    dtrain = xgb.DMatrix(data=X_train, label=y_train)
    des = xgb.DMatrix(data=X_es, label=y_es)
    dtest = xgb.DMatrix(data=X_test, label=y_test)

    final_model = xgb.train(
        params=best_params,
        dtrain=dtrain,
        num_boost_round=n_estimators,
        evals=[(des, "validation")],
        #feval=feval,
        #maximize=maximize,
        #early_stopping_rounds=50,
        callbacks=[xgb.callback.EarlyStopping(rounds=50, save_best=True, maximize=False)], # This is the XGBoost 3.1.1 way
        verbose_eval=True
    )

    print("\nFinal best iteration:", final_model.best_iteration)

    # Predict on test set
    y_pred = final_model.predict(dtest)
    print("Final Test MAPE: %.3f %%" % safe_mape(y_test, y_pred))

    plot_prediction(y_test, y_pred)


if __name__ == "__main__":
    main()
