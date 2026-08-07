# Hardware Performance Counters
This repo hosts dataset including performance counters collected on machines in the [counters-table.md](counters-table.md) file.

# Data
- app\_data\_hpc : performance counter data collected while running hpc applications on hpc platforms
  - [histogram.ipynb](histogram.ipynb): Shows the distribution of features
- app\_data\_cloud : performance counter data collected while running hpc applications on cloud platforms
- raja-data: benchmark scores of RAJAPerfSuite collected on various platforms


# Model
- [pipeline1.py](pipeline1.py): xgboost-based regression model tuned via optuna. Samples are prepared via normalization and embedding using RobustScaler, PowerTransformer and TabNet.
```text
 ┌───────────────────────────┐      ┌─────────────────────────────────┐
 │ machine data (22 samples) │      │ application data (3500 samples) │
 └───────────────────────────┘      └─────────────────────────────────┘
              │                                     │
              ▼                                     ▼
      PowerTransformer (scaler)             RobustScaler (scaler)
              │                                     │
              │                                     ▼
              │                            TabNetPretrainer.fit()
              │                   (learn embeddings / feature structure)
              │                                     │
              │                                     ▼
              │                          Embeddings for each sample
              │                                     │
              └─────────── Cross-product ───────────┘
                                │
                                ▼
                           Joined data
                                │
                                ▼
           Split data into train (80%) and test (20%) sets
                                │
                                ▼
                Split training into 5-folds for CV
                                │
                                ▼
          XGBoostRegressor/TabNetRegressor.fit(embeddings, y)
                                │
                                ▼
             Regression evaluation with CV validation set,
                      Early stopping decicion
                                │
                                ▼
                    Pick the best hyper-parameters
                                │
                                ▼
    Put 10% of the training set aside for early stopping validation.
                                │
                                ▼
             XGBoostRegressor/TabNetRegressor.fit(embeddings, y)
                                │
                                ▼
                 Evaluate the model on the test set
```
  The above pipeline has a shortcoming due to the cross-validation (CV) driving
  the hyper-parameter search. Training data can only be split into N-folds after
  joining the machine data and the application data while we want to isolate CV
  data partitions from the information on the overall feature distribution.
  Applying scaler before spliting data may leak such information. However,
  this pipeline is computationally efficient, and the scalers fit to the set of
  features with originial distribution without the duplication by joining.

- [pipeline2.py](pipeline2.py):
  The other pipelie is as follows. It is similar to the first one but differs
  in when feature transformation happens. It happens after 5-folds split.
  However, this one takes quite long time for TabNet to fit.
```text
 ┌───────────────────────────┐      ┌─────────────────────────────────┐
 │ machine data (22 samples) │      │ application data (3500 samples) │
 └───────────────────────────┘      └─────────────────────────────────┘
              │                                     │
              │                                     │
              └─────────── Cross-product ───────────┘
                                │
                                ▼
                           Joined data
                                │
                                ▼
            split data into train (80%) and test (20%) sets
                                │
                                ▼
                split training into 5-folds for CV
                                │
                                ▼
              ┌─────────────────────────────────────┐
              │                                     │
              ▼                                     ▼
      PowerTransformer (scaler)              RobustScaler (scaler)
      only on machine featuresa              only on application features
              │                                     │
              └─────────────────────────────────────┘
                                │
                                ▼
                     TabNetPretrainer.fit(X)
              (learn embeddings / feature structure)
                                │
                                ▼
                     Embeddings for each sample
                                │
                                ▼
            XGBoostRegressor/TabNetRegressor.fit(embeddings, y)
                                │
                                ▼
            Regression evaluation with CV validation set,
                    Early stopping decicion
                                │
                                ▼
                    Pick the best hyper-parameters
                                │
                                ▼
 Use the same techniques as used in CV to fit scalers and TabNet encoder to
 the whole training set. Then, put 10% aside for early stopping validation.
 Apply the scaler and eoncoder to the test samples.
                                │
                                ▼
            XGBoostRegressor/TabNetRegressor.fit(embeddings, y)
                                │
                                ▼
                 Evaluate the model on the test set
```
- [xgboost-models/xgb-reg.ipynb](xgboost-models/xgb-reg.ipynb) :  xgboost-based regression model to the predict relative performance of an app on a target platform based on the set of performance counters collected on a source platform. This model is provided as an example of using the data.

# Required Python Packages
```text
# python 3.12.9
# First install nightly torch with CUDA
# pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu121

# Core scientific stack
numpy>=2.0
pandas>=2.2
scipy>=1.12

# Machine learning and preprocessing
scikit-learn>=1.4
xgboost>=2.0

# Optimization
optuna>=3.6

# Visualization
matplotlib>=3.8
seaborn>=0.13

# Dimensionality reduction
umap-learn>=0.5

# PyTorch + TabNet
# pip install --upgrade git+https://github.com/dreamquark-ai/tabnet.git
pytorch-tabnet>=4.1.0

# Optional but recommended
joblib>=1.4

```
