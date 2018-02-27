'''
script to test a method to save new journals downloaded and retrieve only
those that are not updated
'''

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()
engine = create_engine('sqlite:///test.db')
session = sessionmaker()
session.configure(bind=engine)


'''use the database to decide which items todo'''
'''we use a in memory database to test'''
items_done = ['a','b']
all_items = ['a','b','c']


class Nature(Base):
    __tablename__ = 'nature'
    id = Column(Integer, primary_key=True)
    name = Column(String)

'''create tables'''
Base.metadata.create_all(engine)
s = session()

'''create downloaded items'''
for x in items_done:
    n = Nature(name=x)
    s.add(n)
    s.commit()

'''get all items done'''
done = s.query(Nature).all()

print([x.name for x in done])
