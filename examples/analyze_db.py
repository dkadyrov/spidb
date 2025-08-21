#%%
from spidb import spidb, normalization
import pandas as pd 

db = spidb.Database(r"data/spi.db")

#%%
records = db.session.query(spidb.Record).all()
df = pd.DataFrame([v.__dict__ for v in records])

# make none if the value is None 
df["subject"] = [v.subject.name if v.subject is not None else None for v in records]
df["material"] = [v.material.name if v.material is not None else None for v in records]

# if subject is None, set it to "No Insect"
df["subject"] = df["subject"].fillna("No Insect")
#%%
# create a pivot table of the number of events per subject and material
e = df[df.sensor_id == 2]
e = e[e.noise == "Noise"]

pivot = e.pivot_table(index="subject", columns="material", values="id", aggfunc="count")
# %%
