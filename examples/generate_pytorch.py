#%%
import torch
import torchaudio
import torchaudio.functional as F
import torchaudio.transforms as T

from spidb import spidb 

db = spidb.Database(r"data/spi.db")
#%%
# %%
from spidb import spidb, visualizer
from dankpy import file, dt, dankframe, audio
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.style.use("dankpy.styles.neurips")
# %%
db = spidb.Database(r"data/spi.db")

# Acoustic Sensor
logs = db.session.query(spidb.Log).filter(spidb.Log.sensor == "ASPIDS").all()

logs = dankframe.from_list(logs)
#%%
# create an array from 0 to 7
channels = list(range(8))

time_segment = 60 # seconds

for l, log in logs.iterrows():
    start = log.start + dt.timedelta(seconds=60)
    if log.end - log.start < dt.timedelta(seconds=time_segment):
        end = log.end
    else:
        end = start + dt.timedelta(seconds=time_segment)

    for c in channels: 
        a = db.get_audio(start=start, end=end, sensor="ASPIDS", channel=c)

        # as a dataframe series
        a.data.signal

        # as a np array
        a.audio 

        # as a tensor
        tensor = torch.from_numpy(a.audio)

        transform = T.Spectrogram(
            n_fft=1024, 
            win_length=1024,
            power=2 #magnitude
        )

        spec = transform(tensor)

        spec = 10*np.log10(spec)

        fig, ax = plt.subplots()
        axi = ax.imshow(spec, origin="lower", cmap="jet")
        axi.set_clim(-70, -40)
        ax.axis("off")
        break
    break

#%%
# Microwave Sensor 
logs = db.session.query(spidb.Log).filter(spidb.Log.sensor == "MSPIDS").all()
logs = dankframe.from_list(logs)

channels = list(range(8))

time_segment = 60 # seconds

for l, log in logs.iterrows():
    start = log.start
    if log.end - log.start < dt.timedelta(seconds=time_segment):
        end = log.end
    else:
        end = start + dt.timedelta(seconds=time_segment)

    for c in channels: 
        a = db.get_audio(start=start, end=end, sensor="MSPIDS", channel=c)

        # IF you just want the raw audio data:
        # as a dataframe series
        a.data.signal
        # as a np array
        a.audio

        tensor = torch.from_numpy(a.audio)

        transform = T.Spectrogram(
            n_fft=1024, 
            win_length=1024,
            power=2 #magnitude
        )

        spec = transform(tensor)

        spec = 10*np.log10(spec)

        fig, ax = plt.subplots()
        axi = ax.imshow(spec, origin="lower", cmap="jet")
        axi.set_clim(-100, -70)
        if c < 6:
            ax.set_ylim(0, 200)

        fig.colorbar(axi)

        break

    break 
#%%
