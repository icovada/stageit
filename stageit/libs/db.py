import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, BLOB, DATETIME, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Templates(Base):
    __tablename__ = 'templates'
    id = Column(String(36), primary_key=True)
    name = Column(String(50), nullable=False)
    folder = Column(ForeignKey('templates.id'))
    templatefile = Column(String(50))
    templatedata = Column(BLOB(4096))


class History(Base):
    __tablename__ = 'history'
    id = Column(String(36), primary_key=True)
    serial = Column(String(20))
    datestart = Column(DATETIME)
    dateend = Column(DATETIME)
    templatename = Column(String(50))
    rundata = Column(BLOB(1024000))


# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('sqlite:///sqlalchemy_example.db')


if '__name__' = '__main__':
    Base.metadata.create_all(engine)
