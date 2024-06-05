# %%
from spidb import spidb, visualizer
from dankpy import file, dt, dankframe
import glob
import pandas as pd
import matplotlib.pyplot as plt
import multiprocessing as mp

import os

plt.style.use("dankpy.styles.neurips")
# %%
db = spidb.Database(r"data/spi.db")

# Acoustic Sensor
logs = db.session.query(spidb.Log).filter(spidb.Log.sensor == "ASPIDS").all()

logs = dankframe.from_list(logs)
# %%
# create an array from 0 to 7
channels = list(range(8))

time_segment = 60  # seconds

targets = [
    "Tribolium confusum",
    "Callosobruchus maculatus",
    "Tenebrio molitor larvae",
    "Tenebrio molitor",
]

ignore = ["No Insects (Unconfirmed)"]

#%%

# for l, log in logs.iterrows():
def generate_aspids_images(log):
    start = log.start
    if log.end - log.start < dt.timedelta(seconds=time_segment):
        end = log.end
    else:
        end = start + dt.timedelta(seconds=time_segment)

    if log.target in ignore:
        return

    iteration = 0 
    while end <= log.end: 

        # fig, ax = visualizer.spectrogram_display(
        #     db, start, end, sensor="ASPIDS", section="all", time_format="seconds"
        # )
        # fig.supylabel(None)
        # fig.supxlabel(None)

        # for a in ax:
        #     a.axis("off")

        for c in channels:
            a = db.get_audio(start=start, end=end, sensor="ASPIDS", channel=c)

            # time, frequency, Pxx = a.spectrogram(
            #     window_size=1024,
            #     nfft=1024,
            #     nperseg=1024,
            #     noverlap=512,
            #     time_format="seconds",
            # )

            fig, ax = a.plot_spectrogram(
                window_size=1024,
                nfft=1024,
                nperseg=1024,
                noverlap=512,
                time_format="seconds",
                zmin=-140,
                zmax=-80,
            )
            ax.axis("off")

            if log.target in targets:
                fig.savefig(
                    rf"data/kaggle/ASPIDS/spectrograms/binary/insect/T{log.id} - i{iteration} - {log.target} - {log.material} - {log.noise} C{c}.png",
                    dpi=300,
                )

                os.makedirs(
                    rf"data/kaggle/ASPIDS/spectrograms/multiclass/{log.target}",
                    exist_ok=True,
                )

                fig.savefig(
                    rf"data/kaggle/ASPIDS/spectrograms/multiclass/{log.target}/T{log.id} - i{iteration} - {log.target} - {log.material} - {log.noise} C{c}.png",
                    dpi=300,
                )


            else:
                fig.savefig(
                    rf"data/kaggle/ASPIDS/spectrograms/binary/no_insect/T{log.id} - i{iteration} - {log.target} - {log.material} - {log.noise} C{c}.png",
                    dpi=300,
                )

                fig.savefig(
                    rf"data/kaggle/ASPIDS/spectrograms/multiclass/no_insect/T{log.id} - i{iteration} - {log.target} - {log.material} - {log.noise} C{c}.png",
                    dpi=300,
                )

        start = end
        end = start + dt.timedelta(seconds=time_segment)

        iteration += 1 
        plt.close("all")
    print(f"Log {log.id} complete")


if __name__ == "__main__":
    cpus = mp.cpu_count()
    pool = mp.Pool(cpus)

    # logs = db.session.query(spidb.Log).filter(spidb.Log.sensor == "ASPIDS").all()
    logs = [db.session.get(spidb.Log, 28), db.session.get(spidb.Log, 8), db.session.get(spidb.Log, 52)]

    results = pool.map(generate_aspids_images, logs)

    pool.close()
    pool.join()