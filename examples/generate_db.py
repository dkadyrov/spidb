"""Generate Database

This script demonstrates how to generate a database from the acoustic files and log files. It illustrates how to create a database, add files and logs to the database, and commit the changes.
"""

from spidb import spidb
from dankpy import file, dt
import glob
import pandas as pd
import os 

# Location of database. It will be created if it does not exist.
if os.path.exists("data/spi.db"):
    os.remove("data/spi.db")

db = spidb.Database(r"data/spi.db")

aspids = spidb.Sensor(
    name = "ASPIDS",
    subname = "Acoustic - Stored Product Insect Detection System",
    manufacturer = "STAR Center, Stevens Institute of Technology",
    type_class = "Acoustic",
    number_of_channels=8
)
db.session.add(aspids)
db.session.commit()


# Location of the acoustic files
acoustic_files = glob.glob(r"data/aspids/**/*.wav", recursive=True)

# Get the metadata of the acoustic files
files = file.metadatas(acoustic_files, extended=True, stevens=True)

# Add the files to the database
sonic_files = []
for i, group in files.groupby("channel"):

    channel = spidb.Channel(
        number = i, 
        sensor = aspids
    )

    db.session.add(channel)
    db.session.commit()

    for j, fi in group.iterrows():
        ff = spidb.File(
            filepath=fi.filepath,
            filename=fi.filename,
            extension=fi.extension,
            sample_rate=fi.sample_rate,
            start=fi.start,
            end=fi.end,
            duration=fi.duration,
            channel=channel,
            sensor=aspids,
            channel_number=i
        )

        sonic_files.append(ff)
db.session.add_all(sonic_files)
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
targets = ["Tribolium confusum", "Tenebrio molitor larva", "Tenebrio molitor", "Callosobruchus maculatus"]

events = [] 
for t, row in log.groupby(["target", "material"]):
    s = db.session.query(spidb.Subject).filter(spidb.Subject.name == t[0]).first()

    if s is None:
        s = spidb.Subject(
            name = t[0],
        )
        db.session.add(s)
        db.session.commit()

    m = db.session.query(spidb.Material).filter(spidb.Material.name == t[1]).first()

    if m is None:

        m = spidb.Material(
        name = t[1]
            )
        db.session.add(m)
        db.session.commit()

    for l, r in row.iterrows():
        e = spidb.Event(
            start=r["start"],
            end=r["end"],
            description=r.description,
            noise=r.noise,
            material=m,
            sensor = aspids,
            # subject=s
        )

        events.append(e)

        EveSub = spidb.EventSubject(
            event = e,
            subject = s,
        )

        events.append(EveSub)
db.session.add_all(events)
db.session.commit()


mspids = spidb.Sensor(
    name = "MSPIDS",
    subname = "Microwave - Stored Product Insect Detection System",
    manufacturer = "STAR Center, Stevens Institute of Technology",
    type_class = "Microwave",
    number_of_channels=8
)
db.session.add(mspids)
db.session.commit()

# Location of the microwave files
mspids_files = glob.glob(r"data/mspids/**/*.wav", recursive=True)

# Get the metadata of the microwave files
files = file.metadatas(mspids_files, extended=True, stevens=True)

sonic_files = []
for i, group in files.groupby("channel"):

    channel = spidb.Channel(
        number = i, 
        sensor = mspids
    )

    db.session.add(channel)
    db.session.commit()

    for j, fi in group.iterrows():
        ff = spidb.File(
            filepath=fi.filepath,
            filename=fi.filename,
            extension=fi.extension,
            sample_rate=fi.sample_rate,
            start=fi.start,
            end=fi.end,
            duration=fi.duration,
            channel=channel,
            sensor=mspids,
            channel_number=i
        )

        sonic_files.append(ff)
db.session.add_all(sonic_files)
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

events = [] 
for t, row in log.groupby(["target", "material"]):
    s = db.session.query(spidb.Subject).filter(spidb.Subject.name == t[0]).first()
    if s is None:
        s = spidb.Subject(
            name = t[0],
        )
        db.session.add(s)
        db.session.commit()

    m = db.session.query(spidb.Material).filter(spidb.Material.name == t[1]).first()

    if m is None:

        m = spidb.Material(
        name = t[1]
            )
        db.session.add(m)
        db.session.commit()

    for l, r in row.iterrows():
        e = spidb.Event(
            start=r["start"],
            end=r["end"],
            description=r.description,
            noise=r.noise,
            material=m,
            sensor=mspids
            # subject=s
        )

        events.append(e)

        EveSub = spidb.EventSubject(
            event = e,
            subject = s,
        )

        events.append(EveSub)
db.session.add_all(events)
db.session.commit()
