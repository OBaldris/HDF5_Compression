import h5py
import hdf5plugin
import blosc2
import blosc2_btune
import os
import numpy as np



def btune_compression(filename):
    f = h5py.File(filename, 'r')
    dataset = f['cube']
    dset = dataset[:]


    print(file_size_bytes)

    os.environ['BTUNE_TRACE'] = '1'

    base_dir = os.path.dirname("Z:")

    kwargs = {
        "tradeoff": 1,
        "perf_mode": blosc2_btune.PerformanceMode.DECOMP,
        "models_dir": f"{base_dir}/models/"
    }

    blosc2_btune.set_params_defaults(**kwargs)

    urlpath = "btune_config.b2nd"
    nd = blosc2.asarray(dset, urlpath=urlpath, mode="w", cparams={"tuner": blosc2.Tuner.BTUNE})

    print(f"NDArray successfully created in {urlpath}")

