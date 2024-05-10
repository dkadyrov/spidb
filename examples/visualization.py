# %%
from spidb import spidb, visualizer
from dankpy import file, dt
import glob
import pandas as pd
import matplotlib.pyplot as plt

plt.style.use("dankpy.styles.neurips")
# %%
db = spidb.Database(r"data/spi.db")

logs = db.session.query(spidb.Log).filter(spidb.Log.sensor == "ASPIDS").filter(spidb.Log.target == "Tenebrio molitor").filter(spidb.Log.material == "Rice").all()
log = logs[1]

start = log.start + dt.timedelta(seconds=30)
end = log.start + dt.timedelta(seconds=60)
#%%
fig, ax = visualizer.spectrogram_display(db, start=start, end=end, time_format="seconds", section="internal", showscale="True", sensor="ASPIDS")
for a in ax:
    a.set_ylim(0, 8000)
    a.set_yticks([0, 4000, 8000])
fig.savefig(rf"reports/documents/NeurIPS_SPID/images/spectrogram_display_{log.target}_{log.material}.pdf", dpi=300, bbox_inches="tight")
#%%