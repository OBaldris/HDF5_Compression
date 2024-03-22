import os,  hdf5plugin
import numpy as np
import cbf
import cbf_to_hdf5
import nexus_format


# convert cbf data to hdf5 dataset

cbf_folder = ("/mnt/c/Users/oriol/ALBA/cbf_folder")
hdf5_outpath = ("/mnt/c/Users/oriol/ALBA")
DTYPE = np.uint16
hdf5_outfile = hdf5_outpath +("/")+cbf_folder.split("/")[-1] + ".h5"
print("Outfile:", hdf5_outfile)


#apply conversion to hdf5
convert_cbf_to_hdf5 = cbf_to_hdf5.convert_cbf_to_hdf5(cbf_folder, hdf5_outfile, 0, dtype=DTYPE)



#generate master file
cbf_files = sorted(os.listdir(cbf_folder))
first_element = os.path.join(cbf_folder, cbf_files[0])

h5master_outfile = hdf5_outpath +("/")+cbf_folder.split("/")[-1] + "_master.h5"

metadata=nexus_format.get_experimental_metadata(first_element, h5master_outfile, cbf_folder)





'''
import os, importlib, hdf5plugin
to_hdf5_lib = importlib.import_module("cbf_to_hdf5")
cbf_folder = ("Z:\\cbf_folder")
hdf5_outpath = ("Z:\\")

hdf5_outfile = hdf5_outpath + cbf_folder.split("\\")[-1] + ".hdf5"
test_inputs = (blosc_cnames[0], blosc_clevels[0], blosc_shuffles[0], chunks_list[0]) # Test values
str_test_inputs =  str(", ".join(str(x) for x in test_inputs))
compressor = hdf5plugin.Blosc(cname=test_inputs[0], clevel=test_inputs[1], shuffle=test_inputs[2])

to_hdf5_lib.convert_cbf_to_hdf5(cbf_folder, hdf5_outfile, str_test_inputs, 
                               compressor=compressor, chunks=test_inputs[3], csv_outfile=csv_outpath,
                               uncompressed_mode=uncompressed_mode)
'''