#%%
from spidb import spidb, normalization
import pandas as pd 

db = spidb.Database(r"data/spi.db")

sensor = db.session.query(spidb.Sensor).filter(spidb.Sensor.id == 1).first()

for channel in sensor.channels: 
    if channel.number < 4: 
        c = normalization.noise_coefficient(db, sensor, channel, filter="bandpass", low=500, high=6000, order=10)
    else: 
        c = normalization.noise_coefficient(db, sensor, channel, filter="highpass", low=500, order=10)
    channel.gain = c
    db.session.commit()
#%%
#%%

data = pd.DataFrame()

for channel in sensor.channels: 
    spl = normalization.noise_spl(db, sensor, channel)

    if "frequency" not in data.columns: 
        data["frequency"] = spl["frequency"]

    data[f"Ch. {channel.number}"] = spl["power"]


# %%
