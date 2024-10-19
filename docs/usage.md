# Usage

The SPIDB package uses `SQLAlchemy` syntax to interact with the SQLite database. The package provides a set of classes and functions to manage the data in the database. The following sections provide examples of how to use the SPIDB package to interact with the database.

## Accessing the Database

The database can be accessed using the `Database` class from the `spidb` module. The `Database` class provides methods to interact with the database, such as querying the data, inserting new records, and updating existing records. The following example demonstrates how to initialize the database and access the data:

```python
from spidb import spidb

db = spidb.Database("data/spi.db")
```

## Querying the Database

The `Database` class provides methods to query the data in the database. The `query` method can be used to retrieve records from the database based on specific criteria. The following example demonstrates how to query the database for all the events. 

```python
from spidb import models

events = db.session.query(models.Event).all()
```

## Adding Records to the Database

The following example demonstrates how to add records to the database.

```python
from spidb import spidb, models

db = spidb.Database("data/spi.db")

sensor = db.session.query(models.Sensor).filter(models.Sensor.name == "A-SPIDS").first()
material = db.session.query(models.Material).filter(models.Material.name == "Rice").first()
subject = db.session.query(models.Subject).filter(models.Subject.name == "Mealworm").first()

event = models.Event(
    start="2024-10-18 00:04:20",
    end="2024-10-18 00:04:21",
    description="Mealworm placed in center",
    noise="Silence",
    material=material,
    subject=subject,
    sensor=sensor
)

db.session.add(event)
db.session.commit()
```

## Extracting Audio Data

The `Database` class provides methods to extract audio data from the database. The `get_audio` method can be used to retrieve the audio data associated with a specific event. The following example demonstrates how to extract the audio data for a specific event.

```python
from spidb import spidb, models

db = spidb.Database("data/spi.db")

event = db.session.query(models.Event).filter(models.Event.id == 42).first()

start = event.start
end = event.end

audio = db.get_audio(start, end, sensor=event.sensor, channel_number = 10)
```