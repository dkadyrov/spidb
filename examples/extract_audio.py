#%%
from spidb import spidb 
from dankpy import dt 
import numpy as np
from scipy import signal
import librosa

db = spidb.Database(r"data/spi.db")

sensor = db.session.query(spidb.Sensor).filter(spidb.Sensor.name == "ASPIDS").first()

events = db.session.query(spidb.Event).filter(spidb.Event.sensor == sensor).all()
#%%
channels = [0, 1,2, 3, 4, 5, 6, 7]

targets = [
    "Tribolium confusum",
    "Callosobruchus maculatus",
    "Tenebrio molitor larvae",
    "Tenebrio molitor",
]

ignore = ["No insects (Unconfirmed)", "Callosobruchus maculatus larvae", "A lot of Bugs", "Unknown Insect"]


for event in events: 
    start = event.start
    if event.end - event.start < dt.timedelta(seconds=60):
        end = event.end
    else:
        end = start + dt.timedelta(seconds=60)

# %%
