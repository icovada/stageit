"""Database definition and session generator."""

from sqlalchemy import Column, ForeignKey, String, BLOB, DATETIME
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

BASE = declarative_base()


class Templates(BASE):
    """Defines templates table."""

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


class History(BASE):
    """Defines history table."""

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


class Tasks(BASE):
    """Defines tasks table."""

    __tablename__ = 'tasks'
    pkid = Column(String(36), primary_key=True)
    description = Column(String(50))
    fktemplate = Column(String(50), ForeignKey('templates.pkid'), nullable=False)
    taskvalues = Column(BLOB(4096))

def newsession():
    """Return a new session."""
    return SESSION()

# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
ENGINE = create_engine('sqlite:///stagedb.db', echo=True)
SESSION = sessionmaker(bind=ENGINE)

BASE.metadata.create_all(ENGINE)
