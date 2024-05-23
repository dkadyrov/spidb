# %%
from spidb import spidb, visualizer
from dankpy import file, dt, dankframe
import glob
import pandas as pd
import matplotlib.pyplot as plt

import torch

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
    start = log.start
    if log.end - log.start < dt.timedelta(seconds=time_segment):
        end = log.end
    else:
        end = start + dt.timedelta(seconds=time_segment)

    for c in channels: 
        a = db.get_audio(start=start, end=end, sensor="ASPIDS", channel=c)

        # IF you just want the raw audio data: 
        # as a dataframe series
        a.data.signal
        # as a np array
        a.audio 

        # raw spectrogram values 
        time, frequency, Pxx = a.spectrogram(window_size=1024, nfft=1024, nperseg=1024, noverlap=512, time_format="seconds")

        # convert to tensor
        tensor = torch.from_numpy(Pxx)

        # plot
        fig, ax = a.plot_spectrogram(window_size=1024, nfft=1024, nperseg=1024, noverlap=512, time_format="seconds", zmin=-140, zmax=-80)

        # removing axis and labels
        ax.axis("off")

        # envelope waveform 
        if c < 4:
            a.bandpass_filter(500, 600, overwrite=True)
        else: 
            a.highpass_filter(500, overwrite=True)
        a.envelope(overwrite=True)

        # Normalizing? 
        a.data.signal = a.data.signal / 0.1*a.data.signal.max()
        
        fig, ax = plt.subplots()
        ax.plot(a.data["time [s]"], a.data.signal)
        ax.set_xlim(0, time_segment)
        
        # Maybe need to change the y-axis limits to keep consistent? 
        ax.set_ylim(0, None)

        # Removing axis and labels
        ax.axis("off")


        start = end 
        end = start + dt.timedelta(seconds=time_segment)

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

        # raw spectrogram
        time, frequency, Pxx = a.spectrogram(window_size=1024, nfft=1024, nperseg=1024, noverlap=512, time_format="seconds")

        # convert to tensor
        tensor = torch.from_numpy(Pxx)

        # spectrogram plot
        fig, ax = a.plot_spectrogram(window_size=1024, nfft=1024, nperseg=1024, noverlap=512, time_format="seconds", zmin=-100, zmax=-70)

        # removing axis and labels
        ax.axis("off")

        # envelope waveform and update spectrogram y-axis limits
        if c < 6:
            a.lowpass_filter(200, overwrite=True)
            ax.set_ylim(0, 200)
        else: 
            a.highpass_filter(500, overwrite=True)
            ax.set_ylim(0, 8000)
        a.envelope(overwrite=True)

        # Normalizing? 
        a.data.signal = a.data.signal / 0.1*a.data.signal.max()
        
        fig, ax = plt.subplots()
        ax.plot(a.data["time [s]"], a.data.signal)
        ax.set_xlim(0, time_segment)
        
        # Need to change the y-axis limits to keep consistent
        ax.set_ylim(0, 20)

        # Removing axis and labels
        ax.axis("off")

        start = end 
        end = start + dt.timedelta(seconds=time_segment)

        break

    break 
#%%