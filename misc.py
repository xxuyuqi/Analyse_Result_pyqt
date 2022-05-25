from os.path import splitext, basename
import numpy as np
from scipy.io import loadmat
import h5py


def assem_array(gene_array):
    ele_array = np.ones([120, 100], dtype=int)
    ele_array[10:-10,:] = np.c_[gene_array, gene_array[:,::-1]]
    return ele_array
    

def read_file(fnf):
    suffix  = splitext(fnf)[-1]
    if suffix == '.mat':
        return loadmat(fnf)
    elif suffix == '.hdf5':
        data = {}
        with h5py.File(fnf, 'r') as f:
            for key, value in f.items():
                data[key] = value[()]
            for key, value in f.attrs.items():
                data[key] = value[()]
        return data 
    elif suffix == '.csv':
        return {basename(fnf).split('.')[0] : np.loadtxt(fnf, dtype=float, delimiter=',')}
    elif suffix == '.txt':
        with open(fnf, 'r', encoding='utf-8') as f:
            txt = f.readlines()
        return {basename(fnf).split('.')[0] : txt}
    else:
        return {}