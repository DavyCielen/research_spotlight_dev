import nose

import pandas


s =  u'gr\xe3\xa9gory'
f = {'s':[s]}
df = pd.DataFrame(f)
#df = pandas.read_table(StringIO('Ki\xc3\x9fwetter, Wolfgang;Ki\xc3\x9fwetter, Wolfgang'), sep=";", header=None)
#df["X.1"] = df["X.1"].apply(lambda x : x.decode('utf-8'))
#df.to_csv("blah.csv", encoding="utf-8")

def testMain():
    assert True
