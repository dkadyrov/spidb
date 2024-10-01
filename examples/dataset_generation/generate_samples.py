# %%
from spidb import spidb
from dankpy import dt

# %%
db = spidb.Database(r"data/spi.db")

# %%
files = db.session.query(spidb.models.File).all()

time_segment = 60  # seconds

for file in files:
    start = file.start

    if file.end - file.start < dt.timedelta(seconds=time_segment):
        end = file.end
    else:
        end = start + dt.timedelta(seconds=time_segment)

    while end <= file.end:
        event = (
            db.session.query(spidb.Event)
            .filter(spidb.Event.start <= end)
            .filter(spidb.Event.end >= start)
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
        end = start + dt.timedelta(seconds=time_segment)

db.session.commit()
# %%
