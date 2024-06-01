import os.path

import time

import numpy as np
import pyedflib


def edf_to_arr(edf_path, to_use):

    f = pyedflib.EdfReader(edf_path)
    n = f.signals_in_file
    signal_labels = f.getSignalLabels()
    if signal_labels[:len(to_use)] != to_use: print(signal_labels, edf_path)
    sigbufs = np.zeros((n, f.getNSamples()[0]))
    for i in np.arange(n - 1):
        if signal_labels[i] not in to_use:
            continue

        sigbufs[i, :] = f.readSignal(i)

    return signal_labels, sigbufs


def fix_start_time(filename):
    data = None

    with open(filename, encoding="ISO-8859-1", mode="r") as file:
        data = file.read()
        data = data.replace(":", ".", 2)
    with open(filename, mode="w") as file:
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




