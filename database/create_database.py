from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

''' creates and documents database '''

Base = declarative_base()
engine = create_engine('sqlite:///../tests/test.db')
session = sessionmaker()
session.configure(bind=engine)

class Nature(Base):
    __tablename__ = 'nature'
    id = Column(Integer, primary_key=True)
    name = Column(String)

class Science(Base):
    __tablename__ = 'science'
    id = Column(Integer, primary_key = True)
    name = Column(String)

class Test(Base):
    __tablename__ = 'test'
    id = Column(Integer, primary_key = True)
    name = Column(String)

class Source(Base):
    __tablename__ = 'source'
    id = Column(Integer, primary_key = True)
    ''' url to download from '''
    url = Column(String)
    sourceType = Column(String)
    ''' type of journal, nature, science??'''
    status = Column(String)
    ''' is the source downloaded or not? [done, ignore, failed, todo]'''
    pageHTML = Column(String)

'''create tables'''
Base.metadata.create_all(engine)
