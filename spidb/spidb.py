# %%
from sonicdb import sonic, models
from sqlalchemy import Integer, Column, String, Float, ForeignKey
from sqlalchemy.orm import relationship


class Subject(models.Subject):
    scientific_name = Column(String)
    common_name = Column(String)
    life_cycle = Column(String)
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

    noise = Column(String)


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

    __mapper_args__ = {
        "polymorphic_identity": "material",
    }


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

    __mapper_args__ = {
        "polymorphic_identity": "spidb_sensor",
    }


class Database(sonic.Database):
    def __init__(self, db):
        super().__init__(db)
