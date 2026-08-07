# xAMM
---
This is repository of the paper xAMM: “Attention” to Details Improves Cross-Platform Prediction Accuracy. 

## About
---
We have used embeddings to convert the raw data into embeddings and use prediction tools like XgBoost to predict and analyze realtive runtime of application. Before prediction of application runtime, we supply it with machine information.

## Preparing the environment
``` 
python -m venv /path/to/new/virtual/environment
```
and install all necessary dependencies using 
````
pip install ....
````
## Data 
There are 2 datasets used 
1. Application dataset :Application datasets have information about hardware performance counters for a machine when they have application like laghos that runs on a machine like quartz. 

2. Machine dataset: It consists hardware performance counters are collected from the respective machines using the rajaperfvarsuite as benchmark tool and there performance counters results(PAPI). 

<!-- xAMM/
├── Attention/
│   ├── weighted_Attention.py
│   ├── variance_Attention.py
├── Data
├── ├── ice4hpc/one-out/
├── ice4hpc/
├── ├── results/
├── ├── src/
├── ├── yaml/
├── Plotly_graphs
├── ├── graphs.py
├── pytorch_tabnet
├── ├── generateEmbeddings.py -->

## Folder Structure
```text
xAMM/
├── Attention/
│   ├── weighted_Attention.py
│   └── variance_Attention.py
├── Data/
│   └── ice4hpc/
│       └── one-out/
├── ice4hpc/
│   ├── results/
│   ├── src/
│   └── yaml/
├── Plotly_graphs/
│   └── graphs.py
└── pytorch_tabnet/
    └── generateEmbeddings.py
```
To follow the process of xAMM, you need to follow, following steps.
1. Go to pytorch_tabnet to generate embeddings for both application and machines
2. Go to Attention to generate single AMM for machines 
3. Concatenate the application AMM with single AMM for machines and save the data
4. Apply the prediction performance using ice4hpc repo
To read in detail about the paper we will post link to the paper afterwards

## Reference
CCGRID 2025

## Authors 
* [Aakash Raj Dhakal](https://github.com/RajAakash)
* [Arunavo Dey](https://github.com/ArunavoDey)
* [Tanzima Islam](https://github.com/tzislam)

## Acknowledgements
* Jae-Seung Yeom
* Tapasya Patki

