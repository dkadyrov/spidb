# %%
from spidb import spidb, visualizer
from dankpy import file, dt, colors
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

plt.style.use("dankpy.styles.neurips")
# %%
db = spidb.Database(r"data/spi.db")

# logs = db.session.query(spidb.Log).filter(spidb.Log.sensor == "ASPIDS").filter(spidb.Log.target == "Tribolium confusum").filter(spidb.Log.material == "Flour").all()
# log = logs[-1]

# start = log.start + dt.timedelta(seconds=6.75*60)
# end = start + dt.timedelta(seconds=60)
# #%%
# fig, ax = plt.subplots()
# for c in [0, 1, 2, 3]:
#     audio = db.get_audio(start=start, end=end, sensor="ASPIDS", channel=c)
#     f, p = signal.welch(audio.data.signal, fs=audio.sample_rate, nperseg=1024, scaling="spectrum")
#     ax.plot(f, 10*np.log10(p), label=f"Ch. {c}", c=colors[c])
# ax.legend(loc="upper right", ncols=4)
# ax.set_xlim(0, 12000)
# ax.set_ylim(-125, -25)
# ax.set_xlabel("Frequency [Hz]")
# ax.set_ylabel("Magnitude [dB]")
# ax.set_yticks([-125, -75, -25])
# fig.savefig(rf"reports/documents/NeurIPS_SPID/images/spectra_{log.target}_{log.material}.pdf", dpi=300, bbox_inches="tight")

# #%%
# fig, ax = visualizer.spectrogram_display(db, start=start, end=end, time_format="seconds", section="all", showscale="True", sensor="ASPIDS", compressed=True)
# for a in ax:
#     a.set_ylim(0, 8000)
#     a.set_yticks([0, 4000, 8000])
# fig.savefig(rf"reports/documents/NeurIPS_SPID/images/spectrogram_display_{log.target}_{log.material}.pdf", dpi=300, bbox_inches="tight")
# #%%
# audio = db.get_audio(start=start, end=end, sensor="ASPIDS", channel=0)

# fig, ax = plt.subplots(ncols=2)

# audio.plot_waveform(time_format="seconds", ax=ax[0])
# ax[0].set_xlim(0, 60)
# ax[0].set_xlabel("Time [s] \n a")

# audio.bandpass_filter(500, 6000, overwrite=True)
# audio.envelope(overwrite=True)

# # fig, ax = plt.subplots()
# ax[1].plot(audio.data["time [s]"], audio.data.signal)
# ax[1].set_xlim(0, 60)
# ax[1].set_ylim(0, 0.02)
# ax[1].set_xlabel("Time [s] \n b")
# # fig.supylabel("Amplitude")
# # fig.supxlabel("Time [s]")
# fig.savefig(rf"reports/documents/NeurIPS_SPID/images/combined_{log.target}_{log.material}_0.pdf", dpi=300, bbox_inches="tight")
# #%%
# log = db.session.get(spidb.Log, 152)

# start = log.start
# end = start + dt.timedelta(seconds=60)
# audio = db.get_audio(start=start, end=end, sensor="ASPIDS", channel=7)

# fig, ax = audio.plot_spectrogram(time_format="seconds", zmin=-140, zmax=-80)

# #%%
# log = db.session.query(spidb.Log).filter(spidb.Log.sensor == "MSPIDS").filter(spidb.Log.target == "Tenebrio molitor").filter(spidb.Log.material == "Rice").all()[0]

# start = log.start + dt.timedelta(seconds=60)
# end = start + dt.timedelta(seconds=60)

# fig, ax = visualizer.waveform_display(db, start=start, end=end, sensor="MSPIDS", time_format="seconds")
#%%
log = db.session.get(spidb.Log, 168)

start = log.start + dt.timedelta(seconds=4*60)
end = start + dt.timedelta(seconds=60)

fig, ax = visualizer.waveform_display(db, start=start, end=end, sensor="MSPIDS", time_format="seconds", compressed=True, normalize=True, filter=True, envelope=True)
fig.savefig(rf"reports/documents/NeurIPS_SPID/images/microwave_display{log.target}_{log.material}.pdf", dpi=300, bbox_inches="tight")
# %%
