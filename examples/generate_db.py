"""Generate Database

This script demonstrates how to generate a database from the acoustic files and log files. It illustrates how to create a database, add files and logs to the database, and commit the changes.
"""

from spidb import spidb
from dankpy import file, dt
import glob
import pandas as pd


# Location of database. It will be created if it does not exist.
db = spidb.Database(r"data/spi.db")

# Location of the acoustic files
acoustic_files = glob.glob(r"data/aspids/**/*.wav", recursive=True)

# Get the metadata of the acoustic files
files = file.metadatas(acoustic_files, extended=True, stevens=True)

# Add the files to the database
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

# Location of the ASPID Log File
log = pd.read_csv(r"data/aspids/aspids_log.csv")

# Convert the start and end columns to datetime
log["start"] = pd.to_datetime(log["start"])
log["end"] = pd.to_datetime(log["end"])

# Calculate the duration of the logs
log["duration"] = log["end"] - log["start"]

# Strip the leading and trailing whitespaces from the material and target columns
log.material = log.material.str.strip()
log.target = log.target.str.strip()

# Add the logs to the database
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

# Location of the microwave files
mspids_files = glob.glob(r"data/mspids/**/*.wav", recursive=True)

# Get the metadata of the microwave files
files = file.metadatas(mspids_files, extended=True, stevens=True)

# Add the files to the database
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

# Location of the MSPID Log File
log = pd.read_csv(r"data/mspids/mspids_log.csv")

# Convert the start and end columns to datetime
log["start"] = pd.to_datetime(log["start"])
log["end"] = pd.to_datetime(log["end"])

# Calculate the duration of the logs
log["duration"] = log["end"] - log["start"]

# Strip the leading and trailing whitespaces from the material and target columns
log.material = log.material.str.strip()
log.target = log.target.str.strip()

# Add the logs to the database
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
