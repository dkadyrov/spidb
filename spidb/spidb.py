# %%
from sonicdb import models, sonic
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class Subject(models.Subject):
    scientific_name = Column(String)
    common_name = Column(String)
    life_stage = Column(String)
    weight = Column(Float)  # grams
    height = Column(Float)
    length = Column(Float)
    width = Column(Float)
    volume = Column(Float)
    density = Column(Float)

    events = relationship(
        "spidb.Event", back_populates="subject", enable_typechecks=False
    )

    __mapper_args__ = {
        "polymorphic_identity": "spidb_subject",
    }


class Sample(models.Sample):
    material_id = Column(Integer, ForeignKey("material.id"))
    material = relationship(
        "spidb.Material", back_populates="samples", enable_typechecks=False
    )

    classifications = relationship(
        "spidb.Classification", back_populates="sample", enable_typechecks=False
    )

    noise = Column(String)

    __mapper_args__ = {
        "polymorphic_identity": "spidb_sample",
    }


class Record(models.Record):
    material_id = Column(Integer, ForeignKey("material.id"))
    material = relationship(
        "spidb.Material", back_populates="records", enable_typechecks=False
    )

    noise = Column(String)

    classifications = relationship(
        "spidb.Classification", back_populates="record", enable_typechecks=False
    )

    external_spl = Column(Float)  # SPL dBA
    result = Column(String)  # e.g. "detected", "not_detected"

    # TODO add detection function
    # TODO add figure generation functions (spectrogram, waveform, detection display)

    __mapper_args__ = {
        "polymorphic_identity": "spidb_record",
    }


class Classification(models.Base):
    __tablename__ = "classification"

    id = Column(Integer, primary_key=True)
    datetime = Column(DateTime)
    classifier = Column(String)
    classification = Column(String)

    sensor_id = Column(Integer, ForeignKey("sensor.id"))
    sensor = relationship(
        "spidb.Sensor", back_populates="classifications", enable_typechecks=False
    )

    sample_id = Column(Integer, ForeignKey("sample.id"))
    sample = relationship(
        "spidb.Sample", back_populates="classifications", enable_typechecks=False
    )

    record_id = Column(Integer, ForeignKey("record.id"))
    record = relationship(
        "spidb.Record", back_populates="classifications", enable_typechecks=False
    )

    __mapper_args__ = {
        "polymorphic_identity": "spidb_classification",
    }


class Material(models.Base):
    __tablename__ = "material"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    scientific_name = Column(String)
    common_name = Column(String)
    density = Column(Float)

    events = relationship(
        "spidb.Event", back_populates="material", enable_typechecks=False
    )

    samples = relationship(
        "spidb.Sample", back_populates="material", enable_typechecks=False
    )

    records = relationship(
        "spidb.Record", back_populates="material", enable_typechecks=False
    )

    __mapper_args__ = {
        "polymorphic_identity": "material",
    }

    def __repr__(self):
        return f"<Material(name={self.name}, scientific_name={self.scientific_name}, common_name={self.common_name}, density={self.density})>"


class Event(models.Event):
    material_id = Column(Integer, ForeignKey("material.id"))
    material = relationship(
        "spidb.Material", back_populates="events", enable_typechecks=False
    )

    sensor_id = Column(Integer, ForeignKey("sensor.id"))
    sensor = relationship(
        "spidb.Sensor", back_populates="events", enable_typechecks=False
    )

    noise = Column(String)

    __mapper_args__ = {
        "polymorphic_identity": "spidb_event",
    }


class Sensor(models.Sensor):
    events = relationship(
        "spidb.Event", back_populates="sensor", enable_typechecks=False
    )

    classifications = relationship(
        "spidb.Classification", back_populates="sensor", enable_typechecks=False
    )

    __mapper_args__ = {
        "polymorphic_identity": "spidb_sensor",
    }


class Database(sonic.Database):
    def __init__(self, db):
        super().__init__(db)
        self.record_duration = 60  # seconds
