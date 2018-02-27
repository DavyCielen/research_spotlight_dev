''' see if we can connect to a database already created '''
from sqlalchemy import (create_engine, inspect)

db_uri = 'sqlite:///test.db'
engine = create_engine(db_uri)
inspector = inspect(engine)

''' are the tables present? '''
print(inspector.get_table_names())


''' alternative method'''
from sqlalchemy import MetaData, Table

metadata = MetaData(engine, reflect = True)
print(metadata.tables)
print(metadata.tables['nature'])

'''insert data for test'''
nature = metadata.tables['nature']
ins = nature.insert().values(name='test2')
conn = engine.connect()
conn.execute(ins)
