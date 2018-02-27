'''
use dataset to manipulate data instead of sqlalchemy
https://media.readthedocs.org/pdf/dataset/latest/dataset.pdf
'''

import dataset

'''connect to dataset'''
db = dataset.connect('sqlite:///test.db')

'''find the table nature'''
nature = db['nature']

'''find an object'''
test = db.find(name='test')
print([x["name"] for x in test])

'''update if exists, else insert'''
nature.upsert({'name':'test'}, 'name')
