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
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String(50))
    platform = Column(String(30), nullable=False)
    template = Column(String(20000))
    templatevalues = Column(BLOB(4096))
    filepath = Column(String(256))
    poststaging = Column(String(2048))


class History(Base):
    __tablename__ = 'history'
    pkid = Column(String(36), primary_key=True)
    serial = Column(String(20))
    datestart = Column(DATETIME)
    dateend = Column(DATETIME)
    templatename = Column(String(50))
    rundata = Column(BLOB(1024000))


class Tasks(Base):
    __tablename__ = 'tasks'
    pkid = Column(String(36), primary_key=True)
    description = Column(String(50))
    fktemplate = Column(String(50), ForeignKey('templates.pkid'))
    taskvalues = Column(BLOB(4096))

def newsession():
    return Session()

# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('sqlite:///stagedb.db', echo=True)
Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)
