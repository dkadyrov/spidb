#%%
from spidb import spidb, normalization
from dankpy import acoustics

db = spidb.Database(r"data/spi.db")

#%%

records = db.session.query(spidb.Record).filter(spidb.Record.sensor_id == 1).all()

for record in records: 
    audio = db.get_audio(record.start, record.end, sensor=record.sensor, channel_number=7)
    spl = acoustics.calculate_spl_dba(audio.data.signal, audio.sample_rate)
    spl = normalization.spl_coefficient(spl)
    record.external_spl = spl
db.session.commit()