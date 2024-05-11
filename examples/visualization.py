# %%
from spidb import spidb, visualizer
from dankpy import file, dt
import glob
import pandas as pd
import matplotlib.pyplot as plt

plt.style.use("dankpy.styles.neurips")
# %%
db = spidb.Database(r"data/spi.db")

logs = db.session.query(spidb.Log).filter(spidb.Log.sensor == "ASPIDS").filter(spidb.Log.target == "Tribolium confusum").filter(spidb.Log.material == "Flour").all()
log = logs[-1]

start = log.start + dt.timedelta(seconds=6.75*60)
end = start + dt.timedelta(seconds=60)
#%%
fig, ax = visualizer.spectrogram_display(db, start=start, end=end, time_format="seconds", section="all", showscale="True", sensor="ASPIDS")
for a in ax:
    a.set_ylim(0, 8000)
    a.set_yticks([0, 4000, 8000])
fig.savefig(rf"reports/documents/NeurIPS_SPID/images/spectrogram_display_{log.target}_{log.material}.pdf", dpi=300, bbox_inches="tight")
#%%
audio = db.get_audio(start=start, end=end, sensor="ASPIDS", channel=0)

fig, ax = audio.plot_waveform(time_format="seconds")
ax.set_ylim(-1, 1)
fig.savefig(rf"reports/documents/NeurIPS_SPID/images/waveform_{log.target}_{log.material}_0.pdf", dpi=300, bbox_inches="tight")
#%%
audio.bandpass_filter(500, 8000, overwrite=True)
audio.envelope(overwrite=True)

fig, ax = plt.subplots()
ax.plot(audio.data["time [s]"], audio.data.signal)
ax.set_xlim(0, 60)
ax.set_ylim(0, None)
ax.set_xlabel("Time [s]")
ax.set_ylabel("Amplitude")
fig.savefig(rf"reports/documents/NeurIPS_SPID/images/envelope_{log.target}_{log.material}_0.pdf", dpi=300, bbox_inches="tight")
#%%
log = db.session.get(spidb.Log, 152)

start = log.start
end = start + dt.timedelta(seconds=60)
audio = db.get_audio(start=start, end=end, sensor="ASPIDS", channel=7)

fig, ax = audio.plot_spectrogram(time_format="seconds", zmin=-140, zmax=-80)

#%%
log = db.session.query(spidb.Log).filter(spidb.Log.sensor == "MSPIDS").filter(spidb.Log.target == "Tenebrio molitor").filter(spidb.Log.material == "Rice").all()[0]

start = log.start + dt.timedelta(seconds=60)
end = start + dt.timedelta(seconds=60)

fig, ax = visualizer.waveform_display(db, start=start, end=end, sensor="MSPIDS", time_format="seconds")
#%%
log = db.session.get(spidb.Log, 168)

start = log.start + dt.timedelta(seconds=4*60)
end = start + dt.timedelta(seconds=60)

fig, ax = visualizer.waveform_display(db, start=start, end=end, sensor="MSPIDS", time_format="seconds")
# %%
