#%%
from spidb import spidb, normalization
from datetime import timedelta 
from dankpy import acoustics

db = spidb.Database(r"data/spi_2m.db")

#%%
# remove all records
db.session.query(spidb.Record).delete()
db.session.commit()

# remove all samples
db.session.query(spidb.Sample).delete()
db.session.commit()
#%%
events = db.session.query(spidb.Event).all()
# events = [46, 47, 48, 49]

# events = [
#     db.session.query(spidb.Event).filter(spidb.Event.id == e).first() for e in events
# ]

#%%
db.record_duration = 120  # seconds
duration = db.record_duration

#%%
records = [] 
for event in events: 
    start = event.start
    end = start + timedelta(seconds=duration)

    while end <= event.end: 
        record = spidb.Record(
            start = start,
            end = end,
            event = event,
            sensor = event.sensor,
            subject = event.subject,
            material = event.material,
            noise = event.noise,
        )
        start = end
        end = start + timedelta(seconds=duration)
        records.append(record)
db.session.add_all(records)
db.session.commit()
#%%