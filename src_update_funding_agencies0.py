# coding: utf-8

# ## scripts to updata data

import pandas as pd
import sqlite3 as sqLite
import ast
import time
import random
import datetime


from src import crossref_parse_metadata
from src import crossref_parse_funding
from src import crossref_get_records_byfunder

from src import rss_get_feeds
from src import selenium_get_urls
from src import get_doi

from src import altmetrics_get_by_doi
from src import altmetrics_parse_data



'''
**  SET PATH TO THE DATABASE 
'''
xDB = '/media/SSD_960/___DATA_STAGING/_research_spotlight/research_spotlight.db'
#xDB = '/media/mike/SSD_Data/__data_staging/research_spotlight.db'
xDBCon_pd = 'sqlite:///' + xDB  # Connection to use with pandas (for quick reading)



'''
--------------------------------------------------------------
STEP 2 : UPDATE publications records from selected funding agencies 
---------------------------------------------------------------
'''

def res_pub_funder_monitor():
    '''
    update crossref pub from selected funding agencies
    :return:
    '''


    # get list of funders to monitor
    xSQL_Stm = 'select * from res_pub_funder_monitor'
    xdf = pd.read_sql(xSQL_Stm, xDBCon_pd)
    xlst_funder_ids = list(xdf.funder_doi)
    print 'funding sources to monitor', len(xlst_funder_ids)
    xlst_funder_ids

    # get last update data
    xsql_lastupdate = 'select lstupd_crossref_funder FROM _last_update'
    xdf_1 = pd.read_sql(xsql_lastupdate, xDBCon_pd)
    x_LAST_UPDATE = xdf_1.values[0][0]
    print x_LAST_UPDATE

    # get list dois already in the db
    xsql_doi = 'SELECT pub_record_doi FROM res_pub_crossref'
    xdf_1 = pd.read_sql(xsql_doi, xDBCon_pd)
    x_lst_doi_in_db = list(xdf_1.pub_record_doi)
    print 'doi in db', len(x_lst_doi_in_db)

    # initalize db connection
    xDBCon = sqLite.connect(xDB)
    xCursor = xDBCon.cursor()


    for xFUNDER_ID in xlst_funder_ids:

        xlst_pubs = crossref_get_records_byfunder(xfunder_doi=xFUNDER_ID, x_last_update=x_LAST_UPDATE)

        print 'records:', len(xlst_pubs), 'funder:', xFUNDER_ID

        # Insert the entries in the db
        for xpubEntry in xlst_pubs:
            if xpubEntry['pub_record_doi'] not in x_lst_doi_in_db:
                xcolumns = ', '.join(xpubEntry.keys())
                xplaceholders = ':' + ', :'.join(xpubEntry.keys())
                xquery = 'INSERT INTO res_pub_crossref (%s) VALUES (%s)' % (xcolumns, xplaceholders)
                # print xquery
                xCursor.execute(xquery, xpubEntry)
                xDBCon.commit()

        time.sleep(3)

    # UPDATE THE LATEST UPDATE TO NOW
    xSQL_Stm = 'UPDATE _last_update SET lstupd_crossref_funder = ?'
    xUPDATE_TIME = datetime.datetime.now().strftime('%Y-%m-%d')
    xDataTuple = (xUPDATE_TIME,)
    xCursor.execute(xSQL_Stm, xDataTuple)
    xDBCon.commit()

    xDBCon.close()

    print 'data from selected funding agencies updated'

