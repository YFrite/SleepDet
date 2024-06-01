import os.path

import time

import numpy as np
import pyedflib
AVAILABLE = ["Fp1-M2", "C3-M2", "O1-M2", "Fp2-M1", "C4-M1", "O2-M1"]


def edf_to_arr(edf_path, to_use):
    f = pyedflib.EdfReader(edf_path)
    signal_labels = f.getSignalLabels()
    sigbufs = np.zeros((6, f.getNSamples()[0]))
    for i in np.arange(len(AVAILABLE)):
        if signal_labels[i] not in to_use:
            continue

        sigbufs[i, :] = f.readSignal(i)
    return signal_labels, sigbufs


def fix_start_time(filename):
    data = None

    with open(filename, encoding="ISO-8859-1", mode="r+") as file:
        data = file.read()
        data = data.replace(":", ".", 2)
        file.seek(0)
        file.write(data)


def parse_edf(filename, features_to_use):

    filepath = os.path.join("uploads", filename)

    if not os.path.isfile(filepath):
        raise FileNotFoundError("Файл не загружен")

    try:
        fix_start_time(filepath)
        signal_labels, arr = edf_to_arr(filepath, features_to_use)
    except Exception as e:
        raise e

    return arr




