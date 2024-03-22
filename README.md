
# HDF5 and CBF compression using BTune
During my internship at ALBA Synchrotron I developed this tools to make use of BTune compression optimization to implement in the crystallography data processing pipeline.
If the sensor's output is given as HDF5, BTune and Blosc can be run directly. If the data is CBF, you must first turn it to HDF5 using the tool below




## Import H5py
In  this file you will find all the needed imports in order to work with HDF5 as well as Blosc and BTune.

## Data 
The data used for testing this tools was produced in experiments at ALBA. Any other protein crystallography dataset to be found in Zenodo would also be appropiate for testing. 
## BTune    
BTune is a genetic algorithm that optimizes the parameters and algorithms for compression in the Blosc library that drastically improves compression ratio, speed or both. The btune_function file is a simple implementation of this algorithm
## CBF to HDF5
To transform data from CBF to HDF5 and run BTune on it, a specific tool was created. This takes a folder containing cbf frames and creates a HDF5 containing all of this data in a single or multiple files. To add metadata, see Nexus. 
## Nexus
In order to create a master file in HDF5 that includes metadata in the Nexus format of crystallography, the nexus file takes the info provided in the cbf master file and interprets the parameters present to obtain the Nexus valid format.
## Authors

- [@OBaldris](https://github.com/OBaldris)

