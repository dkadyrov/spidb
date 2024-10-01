""" Visualization 

This script provides examples of how to visualize the data stored in the SPIDB database. The script demonstrates how to display the waveform, spectrogram, and spectra of the audio and microwave sensors. The script also provides examples of how to extract audio data from the database and display the waveform and envelope of the audio signal.
"""
#%%
from spidb import spidb, visualizer
from dankpy import file, dt, colors
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

plt.style.use("dankpy.styles.latex")
# Initialize the Database
db = spidb.Database(r"data/spi.db")

#%%

sensor = db.session.query(spidb.Sensor).filter(spidb.Sensor.name == "ASPIDS").first()

subject = db.session.query(spidb.Subject).filter(spidb.Subject.name == "Tribolium confusum").first()

material = db.session.query(spidb.Material).filter(spidb.Material.name == "Flour").first()

events = db.session.query(spidb.Event).filter(spidb.Event.sensor == sensor).filter(spidb.Event.subject == subject).filter(spidb.Event.material == material).all()

# Get the last event
event = events[-1]

# Find a good time period to display the data
start = event.start + dt.timedelta(seconds=6.75 * 60)
end = start + dt.timedelta(seconds=60)

# Plot the Spectra of the Audio Sensor
fig, ax = plt.subplots()
for c in [0, 1, 2, 3]:
    audio = db.get_audio(start=start, end=end, sensor=sensor, channel_number=c)
    f, p = signal.welch(
        audio.data.signal,
        fs=audio.sample_rate,
        nperseg=1024,
        scaling="spectrum",
        window="blackmanharris",
    )
    ax.plot(f, 10 * np.log10(p), label=f"Ch. {c}", c=colors[c])
ax.legend(loc="upper right", ncols=4)
ax.set_xlim(0, 12000)
ax.set_ylim(-125, -25)
ax.set_xlabel("Frequency [Hz]")
ax.set_ylabel("Magnitude [dB]")
ax.set_yticks([-125, -75, -25])

fig.savefig(rf"C:\Users\daniel\Documents\sonic\projects\publication\figures\spids\visualization/{event.id} - {event.subject.name} - {event.material.name} - spectra.pdf", dpi=300)

#%%

# Spectrogram Display of the Audio Sensor
fig, axs = visualizer.spectrogram_display(
    db,
    start=start,
    end=end,
    time_format="seconds",
    section="all",
    showscale=True,
    sensor=sensor,
    compressed=True,
)
for ax in axs:
    ax.set_ylim(0, 8000)
    ax.set_yticks([0, 4000, 8000])

fig.savefig(rf"C:\Users\daniel\Documents\sonic\projects\publication\figures\spids\visualization/{event.id} - {event.subject.name} - {event.material.name} - spectrogram.pdf", dpi=300)


#%%

# Example of extracting audio
audio = db.get_audio(start=start, end=end, sensor=sensor, channel_number=0)

# Plotting the Waveform and Envelope
fig, ax = plt.subplots(ncols=2)

audio.plot_waveform(time_format="seconds", ax=ax[0])
ax[0].set_xlim(0, 60)
ax[0].set_xlabel("Time [s] \n a")

# Filter the audio signal
audio.bandpass_filter(500, 6000, overwrite=True, order=10)

# Envelope the audio signal
audio.envelope(overwrite=True)

# Normalize the audio signal
level = np.median(audio.data.signal)
noise = audio.data[audio.data.signal <= level]
audio.data.signal = audio.data.signal / np.sqrt(np.mean(noise.signal**2))

ax[1].plot(audio.data["seconds"], audio.data.signal)
ax[1].set_xlim(0, 60)
ax[1].set_xlabel("Time [s] \n b")
ax[1].set_ylim(0, None)

fig, ax = plt.subplots(figsize=(3,1.5))
ax.plot(audio.data["seconds"], audio.data.signal)
ax.set_xlim(0, 60)
ax.set_ylim(0, 400)
ax.set_xlabel("Time [s]")
ax.set_ylabel("Normalized Amplitude")
# fig.savefig(rf"projects/NeurIPS/images/rebuttle/{event.id} - {event.target} - {event.material} - envelope (500-6000).pdf", dpi=300)
#%%
audio = db.get_audio(start=start, end=end, sensor="ASPIDS", channel_number=0)

audio.bandpass_filter(2000, 6000, overwrite=True, order=5)

audio.envelope(overwrite=True)


level = np.median(audio.data.signal)
noise = audio.data[audio.data.signal <= level]
audio.data.signal = audio.data.signal / np.sqrt(np.mean(noise.signal**2))

fig, ax = plt.subplots(figsize=(3,1.5))
ax.plot(audio.data["time [s]"], audio.data.signal)
ax.set_xlim(0, 60)
ax.set_xlabel("Time [s]")
ax.set_ylim(0, 600)
ax.set_ylabel("Normalized Amplitude")
# fig.savefig(rf"projects/NeurIPS/images/rebuttle/{event.id} - {event.target} - {event.material} - envelope (2000-6000).pdf", dpi=300)
#%%
import librosa

audio = db.get_audio(start=start, end=end, sensor=sensor, channel_number=0)


fig, ax = audio.plot_melspectrogram(time_format="seconds", zmin=-60, zmax=-30, showscale="right")
ax.set_ylim(0, 10000)
# fig.savefig(rf"projects/NeurIPS/images/rebuttle/{event.id} - {event.target} - {event.material} - melspectrogram.pdf", dpi=300)


#%%
# Example of extracting audio
event = db.session.get(spidb.Event, 53)

start = event.start
end = start + dt.timedelta(seconds=60)
audio = db.get_audio(start=start, end=end, sensor=sensor, channel_number=7)

fig, ax = audio.plot_spectrogram(time_format="seconds", zmin=-140, zmax=-80)

# Example of a Insect in Microwave Sensor
sensor = db.session.query(spidb.Sensor).filter(spidb.Sensor.name == "MSPIDS").first()

event = db.session.get(spidb.Event, 223)
start = event.start + dt.timedelta(seconds=4*60)
end = start + dt.timedelta(seconds=60)

fig, ax = visualizer.waveform_display(db, start=start, end=end, sensor=sensor, time_format="seconds", compressed=True, normalize=True, filter=True, envelope=True)

fig, ax = visualizer.spectrogram_display(
    db, start=start, end=end, sensor=sensor, time_format="seconds", compressed=True
)

# Waveform Display of the Microwave Sensor
fig, ax = visualizer.waveform_display(
    db,
    start=start,
    end=end,
    sensor=sensor,
    time_format="seconds",
    compressed=True,
    normalize=True,
    filter=True,
    envelope=True,
)

# Spectrograms of the Microwave Sensor
fig, ax = visualizer.spectrogram_display(
    db,
    start=start,
    end=end,
    sensor=sensor,
    time_format="seconds",
    section="all",
    showscale="True",
    compressed=True,
    zmin=-100,
    zmax=-50,
)

# Spectrogram of the Microwave Sensor with a specific channel
microwave = db.get_audio(start=start, end=end, sensor=sensor, channel_number=4)
fig, ax = microwave.plot_spectrogram(zmin=-100, zmax=-50, time_format="seconds")
ax.set_ylim(0, 200)

microwave.lowpass_filter(200, overwrite=True)

microwave.envelope(overwrite=True)
microwave.data.signal = microwave.data.signal / 0.1 * microwave.data.signal.max()

fig, ax = plt.subplots()
ax.plot(microwave.data["time [s]"], microwave.data.signal)
ax.set_xlim(0, 60)
ax.set_ylim(0, 20)

# Example of a Noisy Microwave Moment
event = db.session.get(spidb.Event, 189)
start = event.start + dt.timedelta(seconds=0)
end = start + dt.timedelta(seconds=60)

fig, ax = visualizer.spectrogram_display(
    db,
    start,
    end,
    sensor=sensor,
    section="all",
    time_format="seconds",
    zmin=-100,
    zmax=-50,
)
ax[-1].set_ylim(0, 2000)
ax[-2].set_ylim(0, 2000)
#%%