#%% 
from spidb import spidb, lookup
from dankpy import dankframe
import pandas as pd 
import numpy as np

db = spidb.Database(r"data/spi.db")
#%%
logs = db.session.query(spidb.Log).all()

#%%
aspids = db.session.query(spidb.Log).filter(spidb.Log.sensor == "ASPIDS").all()
aspids = dankframe.from_list(aspids)

aspids = aspids[aspids.target.isin(lookup.lookup.keys())]

silent = aspids[aspids.noise == "Silence"]
noisy = aspids[aspids.noise != "Silence"]


table = pd.pivot_table(silent, values="duration", index="target", columns="material", aggfunc=np.sum, fill_value=0)
table/60


table = pd.pivot_table(noisy, values="duration", index="target", columns="material", aggfunc=np.sum, fill_value=0)
table/60


#%%

mspids = db.session.query(spidb.Log).filter(spidb.Log.sensor == "MSPIDS").all()
mspids = dankframe.from_list(mspids)

mspids = mspids[mspids.target.isin(lookup.lookup.keys())]
table = pd.pivot_table(mspids, values="duration", index="target", columns="material", aggfunc=np.sum, fill_value=0)
table/60
# %%
silent = mspids[mspids.noise == "Silence"]
noisy = mspids[mspids.noise != "Silence"]


table = pd.pivot_table(silent, values="duration", index="target", columns="material", aggfunc=np.sum, fill_value=0)
table/60
#%%

table = pd.pivot_table(noisy, values="duration", index="target", columns="material", aggfunc=np.sum, fill_value=0)
table/60
# %%
