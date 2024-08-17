# %%
from spidb import spidb, visualizer
from dankpy import file, dt, dankframe
import glob
import pandas as pd
import matplotlib.pyplot as plt
import multiprocessing as mp
from tsdownsample import MinMaxLTTBDownsampler

import os

import numpy as np

db = spidb.Database(r"data/spi2.db")

logs = db.session.query(spidb.Log).filter(spidb.Log.sensor == "MSPIDS").all()

logs = dankframe.from_list(logs)

channels = list(range(8))

time_segment = 60  # seconds

targets = [
    "Tribolium confusum",
    "Callosobruchus maculatus",
    "Tenebrio molitor larvae",
    "Tenebrio molitor",
]

ignore = ["No insects (Unconfirmed)", "Callosobruchus maculatus larvae"]


def generate_MSPIDS_envelopes(log):
    start = log.start
    if log.end - log.start < dt.timedelta(seconds=time_segment):
        end = log.end
    else:
        end = start + dt.timedelta(seconds=time_segment)

    if log.target in ignore:
        return

    iteration = 0

    while end <= log.end:
        for c in channels:
            a = db.get_audio(start=start, end=end, sensor="MSPIDS", channel=c)

            if c < 6:
                a.lowpass_filter(50, order=5, overwrite=True)
            else:
                a.highpass_filter(1000, order=5, overwrite=True)

            a.envelope(overwrite=True)

            if c < 6:
                a.data.signal = a.data.signal / 0.1 * a.data.signal.max()
            else:
                level = np.median(a.data.signal)
                noise = a.data[a.data.signal <= level]
                a.data.signal = a.data.signal / np.sqrt(np.mean(noise.signal**2))

            s_ds = MinMaxLTTBDownsampler().downsample(
                a.data["datetime"], a.data["signal"], n_out=1000
            )

            if log.target in targets:
                np.savetxt(
                    rf"data/kaggle/MSPIDS/envelopes/binary/insect/T{log.id} - i{iteration} - {log.target} - {log.material} - {log.noise} C{c}.csv",
                    s_ds,
                    delimiter=",",
                )

                os.makedirs(
                    rf"data/kaggle/MSPIDS/envelopes/multiclass/insect/{log.target}",
                    exist_ok=True,
                )

                np.savetxt(
                    rf"data/kaggle/MSPIDS/envelopes/multiclass/insect/T{log.id} - i{iteration} - {log.target} - {log.material} - {log.noise} C{c}.csv",
                    s_ds,
                    delimiter=",",
                )

            else:
                np.savetxt(
                    rf"data/kaggle/MSPIDS/envelopes/binary/no_insect/T{log.id} - i{iteration} - {log.target} - {log.material} - {log.noise} C{c}.csv",
                    s_ds,
                    delimiter=",",
                )

                np.savetxt(
                    rf"data/kaggle/MSPIDS/envelopes/binary/no_insect/T{log.id} - i{iteration} - {log.target} - {log.material} - {log.noise} C{c}.csv",
                    s_ds,
                    delimiter=",",
                )

        start = end
        end = start + dt.timedelta(seconds=time_segment)

        iteration += 1
    print(f"Log {log.id} complete")


if __name__ == "__main__":
    cpus = mp.cpu_count()
    pool = mp.Pool(cpus)


    logs = db.session.query(spidb.Log).filter(spidb.Log.sensor == "MSPIDS").all()

    # logs = [db.session.get(spidb.Log, 167), db.session.get(spidb.Log, 168), db.session.get(spidb.Log, 209)]

    results = pool.map(generate_MSPIDS_envelopes, logs)

    pool.close()
    pool.join()
