To do the task of downstream prediction analysis, we can use ice4hpc repo.
To use the repo, follow the following steps:
1. Choose appropriate yaml file with src and target data location fixed
2. Choose the appropriate column as target column in driver.py 
3. Select the models that you want to run using yaml file
4. Check run_ls6.sub file to choose appropariate batch script
5. To run, use 
````
sbatch run_ls6.sub
````
6. The outputs are saved in .o and error are saved in .e file