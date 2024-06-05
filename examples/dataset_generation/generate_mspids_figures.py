# %%
import matplotlib 

matplotlib.use("TkAgg")

from spidb import spidb, visualizer
from dankpy import file, dt, dankframe
import glob
import pandas as pd
import matplotlib.pyplot as plt
import multiprocessing as mp

import os




plt.style.use("dankpy.styles.neurips")
db = spidb.Database(r"data/spi.db")
# db = spidb.Database(r"C:\Users\daniel\Documents\SPIDS\data\spi.db")

targets = [
    "Tribolium confusum",
    "Callosobruchus maculatus",
    "Tenebrio molitor larvae",
    "Tenebrio molitor",
]

ignore = ["No insects (Unconfirmed)", "Callosobruchus maculatus larvae", "A lot of Bugs", "Unknown Insect"]
#%%
def generate_mspids_images(log):
    channels = list(range(8))

    time_segment = 60  # seconds
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
        #     db, start, end, sensor="MSPIDS", section="all", time_format="seconds", zmin=-100, zmax=-50)
        # fig.supylabel(None)
        # fig.supxlabel(None)

        # for a in ax:
        #     a.axis("off")

        for c in channels:
            a = db.get_audio(start=start, end=end, sensor="MSPIDS", channel=c)

            if c < 6: 
                fig, ax = a.plot_spectrogram(
                    window_size=1024,
                    nfft=1024,
                    nperseg=1024,
                    noverlap=512,
                    time_format="seconds",
                    zmin=-100,
                    zmax=-50,
                )
            elif c == 6: 
                fig, ax = a.plot_spectrogram(
                    window_size=1024,
                    nfft=1024,
                    nperseg=1024,
                    noverlap=512,
                    time_format="seconds",
                    zmin=-100,
                    zmax=-50,
                )
            else: 
                fig, ax = a.plot_spectrogram(
                    window_size=1024,
                    nfft=1024,
                    nperseg=1024,
                    noverlap=512,
                    time_format="seconds",
                    zmin=-140,
                    zmax=-80,
                )

            if c < 6:
                ax.set_ylim(0, 200)
            else: 
                ax.set_ylim(0, 2000)

            ax.axis("off")

            if log.target in targets:
                fig.savefig(
                    rf"data/kaggle/MSPIDS/spectrograms/binary/insect/T{log.id} - i{iteration} - {log.target} - {log.material} - {log.noise} C{c}.png",
                    dpi=300,
                )

                os.makedirs(
                    rf"data/kaggle/MSPIDS/spectrograms/multiclass/{log.target}",
                    exist_ok=True,
                )

                fig.savefig(
                    rf"data/kaggle/MSPIDS/spectrograms/multiclass/{log.target}/T{log.id} - i{iteration} - {log.target} - {log.material} - {log.noise} C{c}.png",
                    dpi=300,
                )


            else:
                fig.savefig(
                    rf"data/kaggle/MSPIDS/spectrograms/binary/no_insect/T{log.id} - i{iteration} - {log.target} - {log.material} - {log.noise} C{c}.png",
                    dpi=300,
                )

                fig.savefig(
                    rf"data/kaggle/MSPIDS/spectrograms/multiclass/no_insect/T{log.id} - i{iteration} - {log.target} - {log.material} - {log.noise} C{c}.png",
                    dpi=300,
                )


        start = end
        end = start + dt.timedelta(seconds=time_segment)

        iteration += 1
        plt.close("all")
    print(f"Log {log.id} complete")

#%%

if __name__ == "__main__":
    cpus = mp.cpu_count()
    pool = mp.Pool(cpus)

    # logs = db.session.query(spidb.Log).filter(spidb.Log.sensor == "MSPIDS").all()
    logs = [db.session.get(spidb.Log, 167), db.session.get(spidb.Log, 168), db.session.get(spidb.Log, 209)]

    results = pool.map(generate_mspids_images, logs)
    
    pool.close()
    pool.join()
# %%