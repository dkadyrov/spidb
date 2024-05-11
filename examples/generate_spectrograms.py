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