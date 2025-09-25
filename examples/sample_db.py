#%%
from spidb import spidb 
from datetime import timedelta 

db = spidb.Database(r"data/spi_2m.db")

#%%

records =db.session.query(spidb.Record).all()
# events = [46, 47, 48, 49]

# events = [
#     db.session.query(spidb.Event).filter(spidb.Event.id == e).first() for e in events
# ]

#%
duration = 120 

for record in records:
    start = record.start
    end = start + timedelta(seconds=duration)

    sensor = record.sensor 

    for channel in sensor.channels: 
        
        file = db.session.query(spidb.models.File).filter(spidb.models.File.sensor == sensor).filter(spidb.models.File.channel  == channel).filter(spidb.models.File.start <= end).filter(spidb.models.File.end >= start).first()
        
        s = spidb.Sample(
            event = record.event,
            record = record,
            sensor = sensor,
            channel = channel,
            subject = record.subject,
            datetime = start,  
            file = file,
            material = record.material,
            noise = record.noise
        )

        db.session.add(s)
    start = end
    end = start + timedelta(seconds=duration)
db.session.commit()
#%%