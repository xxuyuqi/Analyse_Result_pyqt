import os
from os.path import join, splitext, basename, relpath
import h5py
import numpy as np
from scipy.io import loadmat
from shutil import rmtree

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
        with open(fnf, 'r', encoding='utf-8') as f:
            attr = f.readlines()[-1][2:]
        ind = basename(fnf).split('.')[0]
        return {ind : np.loadtxt(fnf, dtype=float, delimiter=','), "__attr__":attr}
    elif suffix == '.txt':
        with open(fnf, 'r', encoding='utf-8') as f:
            txt = f.readlines()
        return {basename(fnf).split('.')[0] : txt}
    else:
        return {}


def transfer(root:str)->None:
    hdf5_file_path = root+".hdf5"
    fhdf5 = h5py.File(hdf5_file_path, 'w')
    fhdf5.create_group("evoData")
    for rt, dirs, files in os.walk(root):
        group_name = "/evoData/"+'/'.join(relpath(rt, start=root).split('\\'))
        current_loc = fhdf5[group_name]
        for d in dirs:
            current_loc.create_group(d)
        for f in  files:
            data_dict = read_file(join(rt, f))
            if f.split('.')[0] == "bestInd":
                bestGroup = fhdf5.create_group('bestInd')
                for key, value in data_dict.items():
                    if key[:2] == "__":
                        continue
                    key = key.lower()
                    try:
                        bestGroup.create_dataset(key, data=value, compression='gzip', compression_opts=4)
                    except:
                        bestGroup.create_dataset(key, data=value.astype(object), compression='gzip', compression_opts=4)
                continue
            if f == "G_best.txt" or f == "log.txt":
                name = f.split('.')[0]
                try:
                    fhdf5.create_dataset(name, data=data_dict[name], compression='gzip', compression_opts=4)
                except:
                    fhdf5.create_dataset(name, data=data_dict[name].astype(object), compression='gzip', compression_opts=4)
                continue
            if "Generation" in data_dict:
                del data_dict["Generation"]
            for key, value in data_dict.items():
                if key[:2] == "__":
                        continue
                current_loc.create_dataset(key, data=value, compression='gzip', compression_opts=4)
                if key[:2] == "G-":
                    current_loc[key].attrs["obj"] = data_dict['__attr__']
    fhdf5.close()


if __name__ == "__main__":
    # data_dir = r"C:\Users\uiaiu\Desktop\31"
    # exclude_dir = ["hdf"]
    # for d in os.listdir(data_dir):
    #     if d in exclude_dir:
    #         continue
    #     transfer(join(data_dir, d))
    troot = r"C:\Users\uiaiu\Desktop\32"
    transfer(troot)
