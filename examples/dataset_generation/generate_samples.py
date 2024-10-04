# %%
from spidb import spidb
from datetime import timedelta

# %%
db = spidb.Database(r"data/spi.db")

# %%
files = db.session.query(spidb.models.File).all()

time_segment = 60  # seconds

for file in files:
    start = file.start

    if file.end - file.start < timedelta(seconds=time_segment):
        end = file.end
    else:
        end = start + timedelta(seconds=time_segment)

    while end <= file.end:
        event = (
            db.session.query(spidb.Event)
            .filter(spidb.Event.start <= end)
            .filter(spidb.Event.end >= start)
            .filter(spidb.Event.sensor == file.sensor)
            .all()
        )

        s = spidb.Sample(
            channel=file.channel, sensor=file.sensor, file=file, datetime=start
        )

        if len(event) > 0:
            event = event[0]

            s.event = event
            s.subject = event.subject
            s.material = event.material
            s.noise = event.noise

        db.session.add(s)

        start = end
        end = start + timedelta(seconds=time_segment)

db.session.commit()
# %%
