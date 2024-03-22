import os, re, time
import cbf, h5py, hdf5plugin
import numpy as np



def convert_cbf_to_hdf5(cbf_folder: str, hdf5_outfile: str, uncompressed_mode: int, dtype):
    '''
    cube_pattern = r".+_\d+\.cbf" # Filtering cbf files usable for data cube
    cbf_files = sorted([os.path.join(cbf_folder, f) for f in os.listdir(cbf_folder) if f.endswith('.cbf')])
    cube_files = [file for file in cbf_files if re.match(cube_pattern, file)]
    cube_files= cbf_files
    other_files = [file for file in cbf_files if not re.match(cube_pattern, file)]
    '''
    cbf_files = sorted([os.listdir(cbf_folder)])
    cube_files = [file for file in cbf_files]

    global cbf_data
    cube_data, other_data = read_cbf_folder(cbf_folder)

    # Read the first frame to retrieve the shape
    first_frame = cube_data[0]
    image_shape = first_frame.data.shape

    # Creating an HDF5 file with compression for all images in the cbf files
    nb_frames = len(cube_data)
    cube_shape = (nb_frames,) + image_shape

    start_time = time.time()
    

    with h5py.File(hdf5_outfile, 'w') as f: 
        """ # Non cube data
        for i, other_file in enumerate(other_files): 
            dset = f.create_dataset(str(other_file), cbf.read(other_file).data.shape, 
                                    data=cbf.read(other_file).data, **compressor)  
        """ 
        # Cube data
        dset = f.create_dataset("cube", cube_shape, dtype=dtype) 
        for i, data in enumerate(cube_data):
            frame = data
            dset[i,:,:] = frame  

    elapsed_time = time.time() - start_time
    
    
    # Retrieve sizes
    if uncompressed_mode == 0:
        # get size of .cbf folder
        uncompressed_size = sum(os.path.getsize(os.path.join(root, filename)) for root, _, files in os.walk(cbf_folder) for filename in files)
    elif uncompressed_mode == 1:
        # get size of an uncompressed .hdf5
        global uncompressed_hdf5_size
        if not uncompressed_hdf5_size:
            uncompressed_size = metric_uncompressed_hdf5_size(cbf_files, hdf5_outfile)
        else:
            uncompressed_size = uncompressed_hdf5_size
    hdf5_outfile_size = os.path.getsize(hdf5_outfile) 
   

cbf_data = None # Global variable in order to not read it multiple times with threads

def read_cbf_folder(cbf_folder: str):
    global cbf_data 
    if cbf_data:
        return cbf_data
    cube_pattern = r".+_\d+\.cbf" # Filtering cbf files usable for data cube
    cbf_files = sorted([os.path.join(cbf_folder, f) for f in os.listdir(cbf_folder) if f.endswith('.cbf')])
    cube_files = [file for file in cbf_files if re.match(cube_pattern, file)]
    other_files = [file for file in cbf_files if not re.match(cube_pattern, file)]
    cube_data, other_data = [], []
    cube_data = np.concatenate([cbf.read(cbf_file).data[np.newaxis, :] for cbf_file in cube_files], axis=0)
    try:
        other_data = np.concatenate([cbf.read(cbf_file).data[np.newaxis, :] for cbf_file in other_files], axis=0)
    except ValueError:
        pass
    cbf_data = (cube_data, other_data)
    return cbf_data
        
def csv_metrics(compressorName, results, hdf5Filename, csvFilename):
    
    compressionSpeed, decompressionSpeed, originalSize, compressedSize, ratio = results[0], results[1], results[2], results[3], results[4]
    
    # Open the input and output files
    import csv
    header_file = './gcc-projects/codec-bench-main/CSV_HEADER.txt'
    csvfile = csvFilename + '.csv'

    # Read the header file
    with open(header_file, 'r') as f:
        template = f.read().strip().split('\n')

    # Get the header and data rows
    header = template[0]
    data_rows = template[1:]
    new_data = [compressorName, compressionSpeed, decompressionSpeed, 
                originalSize, compressedSize, ratio, hdf5Filename.split("/")[-1]]
    try:
        needs_header = os.stat(csvfile).st_size == 0
    except:
        needs_header = True

    # Open the output CSV file in append mode
    with open(csvfile, 'a', newline='') as f:

        # Create a CSV writer object
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        if needs_header:
            # Write the header row
            writer.writerow(header.split(','))
        
        writer.writerow(new_data)

uncompressed_hdf5_size = None # Global variable in order to not read it multiple times with threads
        
def metric_uncompressed_hdf5_size(cbf_files, hdf5_outfile):
    # Only for csv_metrics, in order to get the reference for the uncompressed hdf5 file size
    datacube_pattern = r".+_\d+\.cbf"
    datacube_files = [file for file in cbf_files if re.match(datacube_pattern, file)]
    other_files = [file for file in cbf_files if not re.match(datacube_pattern, file)]
    nb_frames = len(cbf_files)
    
    hdf5_outfile = hdf5_outfile + "_uncompressed"
    
    # Read the first frame to retrieve the shape
    first_frame = cbf.read(datacube_files[0])
    image_shape = first_frame.data.shape
    cube_shape = (nb_frames,) + image_shape
    
    with h5py.File(hdf5_outfile, 'w') as f: 
        # Non cube data
        for i, other_file in enumerate(other_files):
            dset = f.create_dataset(str(other_file), cbf.read(other_file).data.shape, 
                                    data=cbf.read(other_file).data) # No compressor
        # Cube data
        dset = f.create_dataset("datacube", cube_shape)

        for i, datacube_file in enumerate(datacube_files):
            frame = cbf.read(datacube_files[i]).data
            dset[i,:,:] = frame    
                    
    hdf5_size = os.path.getsize(hdf5_outfile) 
    os.remove(hdf5_outfile)
    global uncompressed_hdf5_size
    uncompressed_hdf5_size = hdf5_size
    return hdf5_size
    
def metric_hdf5_decompression_time(infile): # is this right decompression metric ?
    start_time = time.time()
    with h5py.File(infile, "r") as f:
        a_group_key = list(f.keys())[0]
        data = list(f[a_group_key])
        ds_obj = f[a_group_key]      # returns as a h5py dataset object
        ds_arr = f[a_group_key][()]  # returns as a numpy array
    return time.time() - start_time



''
