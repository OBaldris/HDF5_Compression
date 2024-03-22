import h5py

# Specify the path to the HDF5 file
file_path = ("C:\\Users\\oriol\\ALBA\\cbf_folder.h5")

# Open the HDF5 file in read mode
with h5py.File(file_path, "r") as file:
    # Get the dimensions of the dataset
    dataset = file["cube"]
    dimensions = dataset.shape

    # Calculate the size of the dataset in bytes
    size = dataset.size * dataset.dtype.itemsize

    # Print the dimensions and size of the dataset
    print("Dimensions:", dimensions)
    print("Size:", size, "bytes")
