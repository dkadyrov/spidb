# %%
from spidb import spidb, visualizer
from dankpy import file, dt, dankframe
import glob
import pandas as pd
import matplotlib.pyplot as plt
import multiprocessing as mp

import os
import numpy as np
from tsdownsample import MinMaxLTTBDownsampler

db = spidb.Database(r"data/spi.db")

logs = db.session.query(spidb.Log).filter(spidb.Log.sensor == "ASPIDS").all()

logs = dankframe.from_list(logs)

channels = list(range(8))

time_segment = 60  # seconds

targets = [
    "Tribolium confusum",
    "Callosobruchus maculatus",
    "Tenebrio molitor larvae",
    "Tenebrio molitor",
]

ignore = ["No insects (Unconfirmed)", "Callosobruchus maculatus larvae", "A lot of Bugs", "Unknown Insect"]

def generate_aspids_envelopes(log):
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
            a = db.get_audio(start=start, end=end, sensor="ASPIDS", channel=c)

            if c < 4:
                a.bandpass_filter(2000, 6000, overwrite=True, order=5)
            else:
                a.highpass_filter(500, overwrite=True, order=5)

            a.envelope(overwrite=True)

            level = np.median(a.data.signal)
            noise = a.data[a.data.signal <= level]
            a.data.signal = a.data.signal / np.sqrt(np.mean(noise.signal**2))

            s_ds = MinMaxLTTBDownsampler().downsample(
                a.data["datetime"], a.data["signal"], n_out=1000
            )

            if log.target in targets:
                np.savetxt(
                    rf"data/kaggle/ASPIDS/envelopes/binary/insect/T{log.id} - i{iteration} - {log.target} - {log.material} - {log.noise} C{c}.csv",
                    s_ds,
                    delimiter=",",
                )

                os.makedirs(
                    rf"data/kaggle/ASPIDS/envelopes/multiclass/insect/{log.target}",
                    exist_ok=True,
                )

                np.savetxt(
                    rf"data/kaggle/ASPIDS/envelopes/multiclass/insect/T{log.id} - i{iteration} - {log.target} - {log.material} - {log.noise} C{c}.csv",
                    s_ds,
                    delimiter=",",
                )

            else:
                np.savetxt(
                    rf"data/kaggle/ASPIDS/envelopes/binary/no_insect/T{log.id} - i{iteration} - {log.target} - {log.material} - {log.noise} C{c}.csv",
                    s_ds,
                    delimiter=",",
                )

                np.savetxt(
                    rf"data/kaggle/ASPIDS/envelopes/binary/no_insect/T{log.id} - i{iteration} - {log.target} - {log.material} - {log.noise} C{c}.csv",
                    s_ds,
                    delimiter=",",
                )

        start = end
        end = start + dt.timedelta(seconds=time_segment)

        iteration += 1
        plt.close("all")
    print(f"Log {log.id} complete")

if __name__ == "__main__":
    cpus = mp.cpu_count()
    pool = mp.Pool(cpus)

    logs = db.session.query(spidb.Log).filter(spidb.Log.sensor == "ASPIDS").all()

    results = pool.map(generate_aspids_envelopes, logs)

    pool.close()
    pool.join()
