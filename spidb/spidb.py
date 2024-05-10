#%%
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy_utils import database_exists
from dankpy import dankframe, audio
from numpy import asarray
import librosa 

Base = declarative_base()

class File(Base):
    __tablename__ = "File"

    id = Column(Integer, primary_key=True)
    filepath = Column(String)
    filename = Column(String)
    extension = Column(String)
    sample_rate = Column(Integer)
    start = Column(DateTime)
    end = Column(DateTime)
    duration = Column(Integer)
    number = Column(Integer)
    channel = Column(Integer)
    sensor = Column(String)

class Log(Base):
    __tablename__ = "Log"

    id = Column(Integer, primary_key=True)
    start = Column(DateTime)
    end = Column(DateTime)
    duration = Column(Integer)
    description = Column(String)
    target = Column(String)
    material = Column(String)
    noise = Column(String)
    sensor = Column(String)

    def get_audio(self, channel=0) -> audio.Audio:
        session = Session.object_session(self)
        files = session.query(File).filter(File.start <= self.end).filter(File.end >= self.start).filter(File.channel==channel).all()

        sample_rate = files[0].sample_rate

        length = abs((self.end - self.start).total_seconds() * sample_rate)
        files = dankframe.read_list(files)

        data = []
        for f, file in files.iterrows():
            offset = (self.start - file.start).total_seconds()

            if offset < 0:
                data.extend([0] * int(-offset * sample_rate))
                offset = 0

            duration = (file.end - self.end).total_seconds()

            if duration < 0:
                if offset >= file.duration: 
                    data.extend(
                        librosa.load(file.filepath, sr=sample_rate)[
                            0
                        ].tolist()
                    )
                else: 
                    data.extend(
                        librosa.load(file.filepath, offset=offset, sr=sample_rate)[
                            0
                        ].tolist()
                    )
            else:
                data.extend(
                    librosa.load(
                        file.filepath,
                        offset=offset,
                        duration=file.duration - duration - offset,
                        sr=sample_rate,
                    )[0].tolist()
                )

            start = file.end

        data.extend([0] * int(length - len(data)))

        return audio.Audio(audio=asarray(data), sample_rate=sample_rate, start=start)

class Database(object):
    def __init__(self, db):
        self.engine = create_engine("sqlite+pysqlite:///{}".format(db))
        if database_exists(self.engine.url):
            Base.metadata.bind = self.engine
        else:
            Base.metadata.create_all(self.engine)
        DBSession = sessionmaker(bind=self.engine, autoflush=False)

        self.session = DBSession()

    def get_audio(self, start, end, sensor=None, channel=0) -> audio.Audio:
        files = self.session.query(File).filter(File.start <= end).filter(File.end >= start).filter(File.channel==channel).all()

        if sensor: 
            files = [f for f in files if f.sensor == sensor]

        if len(files) == 0:
            data = [0] * int((end - start).total_seconds()) * 51200
            return audio.Audio(audio=asarray(data), start=start, sample_rate=51200)

        sample_rate = files[0].sample_rate

        file_start = start

        length = abs((end - start).total_seconds() * sample_rate)
        files = dankframe.from_list(files)

        data = []
        for f, file in files.iterrows():
            offset = (start - file.start).total_seconds()

            if offset < 0:
                data.extend([0] * int(-offset * sample_rate))
                offset = 0

            duration = (file.end - end).total_seconds()

            if duration < 0:
                if offset >= file.duration: 
                    data.extend(
                        librosa.load(file.filepath, sr=sample_rate)[
                            0
                        ].tolist()
                    )
                else: 
                    data.extend(
                        librosa.load(file.filepath, offset=offset, sr=sample_rate)[
                            0
                        ].tolist()
                    )
            else:
                data.extend(
                    librosa.load(
                        file.filepath,
                        offset=offset,
                        duration=file.duration - duration - offset,
                        sr=sample_rate,
                    )[0].tolist()
                )

            start = file.end

        data.extend([0.0] * int(length - len(data)))

        return audio.Audio(audio=asarray(data), sample_rate=sample_rate, start=file_start)

