import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, BLOB, DATETIME, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, session, sessionmaker
from sqlalchemy import create_engine, MetaData

Base = declarative_base()


class Templates(Base):
    __tablename__ = 'templates'
    pkid = Column(String(36), primary_key=True)
    description = Column(String(50))
    filepath = Column(String(256))
    installmode = Column(String(20))
    name = Column(String(50), nullable=False, unique=True)
    platform = Column(String(30), nullable=False)
    poststaging = Column(String(2048))
    template = Column(String(20000))
    templatevalues = Column(BLOB(4096))
    tasks = relationship("Tasks", backref="template")


class History(Base):
    __tablename__ = 'history'
    pkid = Column(String(36), primary_key=True)
    dateend = Column(DATETIME)
    datestart = Column(DATETIME)
    description = Column(String(50))
    installmode = Column(String(20))
    model = Column(String(50))
    os_version = Column(String(300))
    rundata = Column(BLOB(1024000))
    serial = Column(String(20))
    serial_number = Column(String(50))
    template = Column(String(20000))
    templatevalues = Column(BLOB(4096))
    vendor = Column(String(30))


class Tasks(Base):
    __tablename__ = 'tasks'
    pkid = Column(String(36), primary_key=True)
    description = Column(String(50))
    fktemplate = Column(String(50), ForeignKey('templates.pkid'), nullable=False)
    taskvalues = Column(BLOB(4096))

def newsession():
    return Session()

# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('sqlite:///stagedb.db', echo=True)
Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)
