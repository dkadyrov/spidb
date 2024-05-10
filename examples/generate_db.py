# %%
from spidb import spidb
from dankpy import file, dt
import glob
import pandas as pd

# %%
db = spidb.Database(r"data/spi.db")
# %%
acoustic_files = glob.glob(r"data/aspids/**/*.wav", recursive=True)

files = file.metadatas(acoustic_files, extended=True, stevens=True)
#%%
for f, fi in files.iterrows():
    ff = spidb.File(
        filepath=fi.filepath,
        filename=fi.filename,
        extension="wav",
        sample_rate=fi.sample_rate,
        start=fi.start,
        end=fi.end,
        duration=fi.duration,
        number=fi.record_number,
        channel=fi.channel,
        sensor="ASPIDS",
    )

    db.session.add(ff)
db.session.commit()
#%%
log = pd.read_csv(r"data/aspids_log.csv")

log["start"] = log["date"].astype(str) + " " + log["start"].astype(str)
log["end"] = log["date"].astype(str) + " " + log["end"].astype(str)

log["start"] = pd.to_datetime(log["start"])
log["end"] = pd.to_datetime(log["end"])
log["duration"] = log["end"] - log["start"]
log.material = log.material.str.strip()
log.target = log.target.str.strip()

for l, row in log.iterrows():
    ll = spidb.Log(
        start=row["start"],
        end=row["end"],
        duration=row.duration.total_seconds(),
        description=row.description,
        target=row.target,
        material=row.material,
        sensor="ASPIDS",
        noise=row.noise,
    )
    db.session.add(ll)
db.session.commit()

#%%

microwave_files = glob.glob(r"data/mspids/**/*.wav", recursive=True)

files = file.metadatas(microwave_files, extended=True, stevens=True)

for f, fi in files.iterrows():
    ff = spidb.File(
        filepath=fi.filepath,
        filename=fi.filename,
        extension="wav",
        sample_rate=fi.sample_rate,
        start=fi.start,
        end=fi.end,
        duration=fi.duration,
        number=fi.record_number,
        channel=fi.channel,
        sensor="MSPIDS",
    )

    db.session.add(ff)
db.session.commit()

log = pd.read_csv(r"data/mspids_log.csv")

log["start"] = log["date"].astype(str) + " " + log["start"].astype(str)
log["end"] = log["date"].astype(str) + " " + log["end"].astype(str)

log["start"] = pd.to_datetime(log["start"])
log["end"] = pd.to_datetime(log["end"])
log["duration"] = log["end"] - log["start"]

for l, row in log.iterrows():
    ll = spidb.Log(
        start=row["start"],
        end=row["end"],
        duration=row.duration.total_seconds(),
        description=row.description,
        target=row.target,
        material=row.material,
        sensor="MSPIDS",
        noise=row.noise,
    )
    db.session.add(ll)
db.session.commit()
