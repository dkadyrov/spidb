# %%
from spidb import spidb, visualizer
from dankpy import file, dt, dankframe
import glob
import pandas as pd
import matplotlib.pyplot as plt

plt.style.use("dankpy.styles.neurips")
# %%
db = spidb.Database(r"data/spi.db")

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

        # spectrogram 
        fig, ax = a.plot_spectrogram(time_format="seconds", zmin=-140, zmax=-80)

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

        start = end 
        end = start + dt.timedelta(seconds=time_segment)

        break

    break 
#%%
