  # coding: utf-8

# ## scripts to updata data

import pandas as pd
import sqlite3 as sqLite
import ast
import time
import random
import datetime
import uuid


from src import crossref_parse_metadata
from src import crossref_parse_funding
from src import crossref_get_records_byfunder
from src import crossref_get_records_bydoi

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
STEP 3 : UPDATE publications records
---------------------------------------------------------------
'''

def res_pub_crossref_insert_records(xlst_dois):
    # connection using sqlite3 (for inserts
    xDBCon = sqLite.connect(xDB)
    xCursor = xDBCon.cursor()

    for x_doi_str in xlst_dois:
        try:
            x_pub_record = crossref_get_records_bydoi(x_doi_str)
            xDictData = dict.fromkeys(['record_uid', 'record_timestamp', 'pub_record_doi', 'pub_record_crossref_raw'])
            xDictData['record_uid'] = str(uuid.uuid4())
            xDictData['record_timestamp'] = str(datetime.datetime.now())
            xDictData['pub_record_doi'] = x_pub_record['pub_doi']
            xDictData['pub_record_crossref_raw'] = x_pub_record['pub_crossref_raw']
            xcolumns = ', '.join(xDictData.keys())
            xplaceholders = ':' + ', :'.join(xDictData.keys())
            xquery = 'INSERT INTO res_pub_crossref (%s) VALUES (%s)' % (xcolumns, xplaceholders)
            # print xquery
            xCursor.execute(xquery, xDictData)
            xDBCon.commit()
            time.sleep(0.5)
        except:
            pass
    xDBCon.close()

    #print 'all updated'



def res_pub_crossref_insert_records_highlights():
    '''
    add records from highlighted publications

    :return:
    '''

    # get the list of the dois to insert in the table

    xsql_sel = '''SELECT
                     distinct x_doi_highlighted_pub
                  FROM
                   res_pub_highlights
                  where
                  x_doi_highlighted_pub
                  not in
                  (select t1.pub_record_doi from res_pub_crossref AS t1)
               '''

    xdf = pd.read_sql(xsql_sel, xDBCon_pd)

    xlst_dois = list(xdf.x_doi_highlighted_pub)

    print 'dois to update:', len(xlst_dois)

    # add the dois

    res_pub_crossref_insert_records(xlst_dois)

    print '--- records from highlights updated now !'









def res_pub_crossref_update():
    '''
    update records of the table publications records
    '''

    # connection using sqlite3 (for inserts)
    xDBCon = sqLite.connect(xDB)
    xCursor = xDBCon.cursor()

    '''1. --- ADD METADATA   ---- '''

    # Update statememt
    xSQL_UpdateStm_meta = """UPDATE
                             res_pub_crossref
                             SET
                               pub_meta_authors = ?,
                               pub_meta_pubyear = ?,
                               pub_meta_journal = ?,
                               pub_meta_title  = ?,
                               pub_meta_bibref = ?,
                               pub_meta_type  = ?
                             WHERE
                               pub_record_doi = ?
                      """

    # Preparing data for update
    xSQL_stm = '''select
                    t1.pub_record_doi,
                    t1.pub_record_crossref_raw
                  from res_pub_crossref AS t1
                  where t1.pub_meta_bibref is null
                  --limit 10
                  '''

    xdf = pd.read_sql(xSQL_stm, xDBCon_pd)

    # get the metadata from "raw string"

    metadata_LstDict = [crossref_parse_metadata(ast.literal_eval(x1))
                        for x1 in
                        list(xdf.pub_record_crossref_raw)]

    print 'records to update: ', len(metadata_LstDict)

    for xPubRecord in metadata_LstDict:
        # get the tuple data in  order
        xDataTuple = (xPubRecord['art_authors'],
                      xPubRecord['art_pubyear'],
                      xPubRecord['art_journal'],
                      xPubRecord['art_title'],
                      xPubRecord['art_bibref'],
                      xPubRecord['art_type'],
                      xPubRecord['art_doi']
                      )
        # update
        xCursor.execute(xSQL_UpdateStm_meta, xDataTuple)

    xDBCon.commit()
    xDBCon.close()

    print 'updating metadata completed !'


    '''2. --- UPDATE FUNDING INFORMATION  ---- '''

    # connection using sqlite3 (for inserts)
    xDBCon = sqLite.connect(xDB)
    xCursor = xDBCon.cursor()

    # get articles for wich we have no entries in the datatable
    xSQL_stm = '''select
                    t1.pub_record_doi,
                    t1.pub_record_crossref_raw
                  from res_pub_crossref AS t1
                  where
                  t1.pub_record_doi not in (select distinct pub_doi from res_pub_crossref_funding)
                  --limit 10
                  '''
    xdf = pd.read_sql(xSQL_stm, xDBCon_pd)

    xlst_pub_records = list(xdf.pub_record_crossref_raw)

    print 'records to process :', len(xlst_pub_records)

    for xpub_record in xlst_pub_records:
        # to dict
        xpub_record = ast.literal_eval(xpub_record)

        # parse funders
        xlst_funder_data = crossref_parse_funding(xpub_record)

        # match names of fields
        for xdata_funder in xlst_funder_data:
            xdata_funder['pub_doi'] = xdata_funder.pop('art_doi')
            # print xdata_funder

            xcolumns = ', '.join(xdata_funder.keys())
            xplaceholders = ':' + ', :'.join(xdata_funder.keys())

            xSQL_Stm_funders = 'INSERT INTO res_pub_crossref_funding (%s) VALUES (%s)' % (xcolumns, xplaceholders)

            xCursor.execute(xSQL_Stm_funders, xdata_funder)

        xDBCon.commit()

    xDBCon.close()

    print 'funding data inserting completed'
