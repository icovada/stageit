import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, BLOB, DATETIME, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, session
from sqlalchemy import create_engine, MetaData

Base = declarative_base()


class Templates(Base):
    __tablename__ = 'templates'
    id = Column(String(36), primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String(50))
    platform = Column(String(30), nullable=False)
    template = Column(String(20000))
    templatevalues = Column(BLOB(4096))
    filepath = Column(String(256))
    poststaging = Column(String(2048))


class History(Base):
    __tablename__ = 'history'
    id = Column(String(36), primary_key=True)
    serial = Column(String(20))
    datestart = Column(DATETIME)
    dateend = Column(DATETIME)
    templatename = Column(String(50))
    rundata = Column(BLOB(1024000))


class Tasks(Base):
    __tablename__ = 'tasks'
    id = Column(String(36), primary_key=True)
    description = Column(String(50))
    fktemplate = Column(String(36), ForeignKey('templates.id'))
    taskvalues = Column(BLOB(4096))


# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('sqlite:///stagedb.db')
conn = engine.connect()
s = session.Session(bind=engine)
md = MetaData(engine)



if __name__ == '__main__':
    Base.metadata.create_all(engine)
    print("Running as main, creating new database.")
else:
    md.reflect()
    history = md.tables['history']
    templates = md.tables['templates']
    tasks = md.tables['tasks']