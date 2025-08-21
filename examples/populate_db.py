import os
import glob
import pandas as pd 

from spidb import spidb
from sonicdb import models, utilities 

# check if the database file exists
db_path = os.path.join("data", "spi.db")
if not os.path.exists(db_path):
    db = spidb.Database(db_path)
else:
    # delete the existing database file
    os.remove(db_path)
    db = spidb.Database(db_path)

sensors = [ 
    {
        "name": "Acoustic - Stored Product Insect Detection System",
        "subname": "A-SPIDS",
        "manufacturer": "Stevens Institute of Technology",
        "number_of_channels": 8, 
        "type_class": "Acoustic",
    },
    {
        "name": "Microwave - Stored Product Insect Detection System",
        "subname": "M-SPIDS",
        "manufacturer": "Stevens Institute of Technology",
        "number_of_channels": 8,
        "type_class": "Microwave",
    }
]

insects = [
    {
        "name": "Callosobruchus maculatus", 
        "scientific_name": "Callosobruchus maculatus",
        "common_name": "Cowpea Beetle",
        "life_stage": "Imago",
        "length": 4, # mm
        "width": 1, # mm
        "height": 1,  # mm
        "weight": 2.1, # mg
        "volume": 4, # mm3
        "density": 525, # kg/m3
    },
    {
        "name": "Tribolium confusum", 
        "scientific_name": "Tribolium confusum",
        "common_name": "Confused Flour Beetle",
        "life_stage": "Imago",
        "length": 4, # mm
        "width": 2, # mm
        "height": 2,  # mm
        "weight": 1, # mg
        "volume": 16, # mm3
        "density": 625, # kg/m3
    },
    {
        "name": "Tenebrio molitor larva", 
        "scientific_name": "Tenebrio molitor",
        "common_name": "Mealworm",
        "life_stage": "Larva",
        "length": 20, # mm
        "width": 2, # mm
        "height": 2,  # mm
        "weight": 130, # mg
        "volume": 80, # mm3
        "density": 1625, # kg/m3
    },
    {
        "name": "Tenebrio molitor", 
        "scientific_name": "Tenebrio molitor",
        "common_name": "Darkling Beetle",
        "life_stage": "Imago",
        "length": 15, # mm
        "width": 5, # mm
        "height": 3,  # mm
        "weight": 160, # mg
        "volume": 225, # mm3
        "density": 711.1, # kg/m3
    }
]

materials = [ 
    {
        "name": "Rice", 
        "scientific_name": "Oryza sativa",
        "common_name": "Rice",
        "density": 720, # kg/m3
    },
    {
        "name": "Corn Flakes",
        "scientific_name": "Zea mays",
        "common_name": "Corn Flakes",
        "density": 118.35, # kg/m3
    },
    {
        "name": "Oatmeal",
        "scientific_name": "Avena sativa",
        "common_name": "Oatmeal",
        "density": 693.19, # kg/m3
    },
    {
        "name": "Wheat Groats", 
        "scientific_name": "Triticum aestivum",
        "common_name": "Wheat Groats",
        "density": 800, # kg/m3
    },
    {
        "name": "Flour", 
        "scientific_name": "Triticum aestivum",
        "common_name": "Flour",
        "density": 593, # kg/m3
    },
]
#%%
for sensor in sensors: 
    s = spidb.Sensor(number_of_channels=sensor["number_of_channels"]) #db.session.query(spidb.Sensor).filter(spidb.Sensor.subname == sensor["subname"]).first()
    s.name = sensor["name"]
    s.subname = sensor["subname"]
    s.manufacturer = sensor["manufacturer"]
    s.number_of_channels = sensor["number_of_channels"]
    s.type_class = sensor["type_class"]

    for channel in s.channels:
        if s.name == "Acoustic - Stored Product Insect Detection System":
            if channel.number < 4: 
                channel.type_class = "Piezoelectric"
            else:
                channel.type_class = "Acoustic Microphone"

        else: 
            if channel.number < 6:
                channel.type_class = "Microwave"
            elif channel.number == 6:
                channel.type_class = "Acoustic Microphone"
            else:
                channel.type_class = "Piezoelectric"
    db.session.add(s)
    db.session.commit()
#%%
for insect in insects:
    i = spidb.Subject()
    i.name = insect["name"]
    i.scientific_name = insect["scientific_name"]
    i.common_name = insect["common_name"]
    i.life_stage = insect["life_stage"]
    i.length = insect["length"]
    i.width = insect["width"]
    i.height = insect["height"]
    i.weight = insect["weight"]
    i.volume = insect["volume"]
    i.density = insect["density"]
    db.session.add(i)
    db.session.commit()

for material in materials:
    m = spidb.Material()
    m.name = material["name"]
    m.scientific_name = material["scientific_name"]
    m.common_name = material["common_name"]
    m.density = material["density"]
    db.session.add(m)
    db.session.commit()

db.session.close()
#%%
# Import Files
files = glob.glob(r"data/aspids/**/*.wav", recursive=True)
#%%
aspids = db.session.query(spidb.Sensor).filter(spidb.Sensor.subname == "A-SPIDS").first()
if len(files) > 0:
    files = utilities.metadatas(files, extended=True, stevens=True)
    flist = [] 
    for f, file in files.iterrows():
        ff = models.File(
            filepath=file.filepath,
            filename=file.filename,
            extension="wav",
            sample_rate=file.sample_rate,
            start=file.start,
            end=file.end,
            duration=file.duration,
            channel_number=file.channel,
            channel=aspids.channels[file.channel],
            sensor=aspids
        )
        flist.append(ff)
    db.session.add_all(flist)
    db.session.commit()
#%%
events = pd.read_csv("data/aspids/aspids_log.csv")
events["start"] = pd.to_datetime(events["start"])
events["end"] = pd.to_datetime(events["end"])
evs = [] 
for g, group in events.groupby(["target", "material"]):  
    subject = db.session.query(spidb.Subject).filter(spidb.Subject.name == g[0]).first()
    if subject is None:
        subject = spidb.Subject(name=g[0])
        db.session.add(subject)
        db.session.commit()
    material = db.session.query(spidb.Material).filter(spidb.Material.name == g[1]).first()
    if material is None:
        material = spidb.Material(name=g[1])
        db.session.add(material)
        db.session.commit()
    for e, event in group.iterrows():
        ev = spidb.Event(
            start=event["start"],
            end=event["end"],
            subject=subject,
            material=material,
            description=event["description"],
            noise=event["noise"],
            sensor=aspids
        )
        evs.append(ev)
db.session.add_all(evs)
db.session.commit()
    
#%%
files = glob.glob(r"data/mspids/**/*.wav", recursive=True)

mspids = db.session.query(spidb.Sensor).filter(spidb.Sensor.subname == "M-SPIDS").first()
if len(files) > 0:
    files = utilities.metadatas(files, extended=True, stevens=True)
    flist = [] 
    for f, file in files.iterrows():
        ff = models.File(
            filepath=file.filepath,
            filename=file.filename,
            extension="wav",
            sample_rate=file.sample_rate,
            start=file.start,
            end=file.end,
            duration=file.duration,
            channel_number=file.channel,
            channel=mspids.channels[file.channel],
            sensor=mspids
        )
        flist.append(ff)
    db.session.add_all(flist)
    db.session.commit()
# %%
events = pd.read_csv("data/mspids/mspids_log.csv")
events["start"] = pd.to_datetime(events["start"])
events["end"] = pd.to_datetime(events["end"])
evs = [] 
for g, group in events.groupby(["target", "material"]):
    subject = db.session.query(spidb.Subject).filter(spidb.Subject.name == g[0]).first()
    if subject is None:
        subject = spidb.Subject(name=g[0])
        db.session.add(subject)
        db.session.commit()
    material = db.session.query(spidb.Material).filter(spidb.Material.name == g[1]).first()
    if material is None:
        material = spidb.Material(name=g[1])
        db.session.add(material)
        db.session.commit()
    for e, event in group.iterrows():
        ev = spidb.Event(
            start=event["start"],
            end=event["end"],
            subject=subject,
            material=material,
            description=event["description"],
            noise=event["noise"],
            sensor=mspids
        )
        evs.append(ev)
db.session.add_all(evs)
db.session.commit()
#%%