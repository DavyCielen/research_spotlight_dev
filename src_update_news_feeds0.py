# coding: utf-8

# ## scripts to updata data

import pandas as pd
import sqlite3 as sqLite
import ast
import time
import random
import datetime


from src import rss_get_feeds
from src import selenium_get_urls
from src import get_doi


'''
**  SET PATH TO THE DATABASE 
'''
xDB = '/media/SSD_960/___DATA_STAGING/_research_spotlight/research_spotlight.db'
#xDB = '/media/mike/SSD_Data/__data_staging/research_spotlight.db'
xDBCon_pd = 'sqlite:///' + xDB  # Connection to use with pandas (for quick reading)



'''
---------------------------------
STEP 1 : UPDATE NEWS FEED
---------------------------------
'''

def res_news_feeds_fetch():
    '''
    fetching news feeds
    :return: updated table of res_news_feeds
    '''

    '''--- 1. GET RSS FEEDS ---- '''

    # connection using sqlite3 (for inserts)
    xDBCon = sqLite.connect(xDB)
    xCursor = xDBCon.cursor()


    # get list of feeds
    xdf_channels = pd.read_sql('select rss_channel, rss_url from res_news_source', xDBCon_pd)
    # xdf_channels.head()
    xlst_Feeds = zip(xdf_channels.rss_channel, xdf_channels.rss_url)
    print 'sources to query:', len(xlst_Feeds)

    # find the urls which are already in the table/db

    xCursor.execute('''SELECT distinct xfeed_entry_url  from res_news_feeds''')
    xlst_ids_indb = xCursor.fetchall()
    xlst_ids_indb = [x[0] for x in xlst_ids_indb]  # to get the records not as list of tuple but list of urls
    print 'entries in the db:', len(xlst_ids_indb)

    for xFeed in xlst_Feeds:
        print 'processing:', xFeed[1]

        time.sleep(1)
        # get the feeds
        xlst_feeds_online = rss_get_feeds(rss_channel=xFeed[0], rss_url=xFeed[1])
        print '---retrieved:', len(xlst_feeds_online)
        # filter the feeds to ignore those already in the db
        xlst_feeds_insert = [xEntry for xEntry in xlst_feeds_online if xEntry['xfeed_entry_url'] not in xlst_ids_indb]
        print '---inserting:', len(xlst_feeds_insert)

        # Insert the entries in the db
        for xEntry in xlst_feeds_insert:
            xcolumns = ', '.join(xEntry.keys())
            xplaceholders = ':' + ', :'.join(xEntry.keys())
            xquery = 'INSERT INTO res_news_feeds (%s) VALUES (%s)' % (xcolumns, xplaceholders)
            # print xquery
            xCursor.execute(xquery, xEntry)
            xDBCon.commit()

    xDBCon.close()

    print 'updating rss science news completed !'


def res_news_feeds_getfulltext():
    '''
    use selenium to get fulltext
    '''


    '''--- 2. GETfulltext of newsfeeds ---- '''

    # connection using sqlite3 (for inserts)
    xDBCon = sqLite.connect(xDB)
    xCursor = xDBCon.cursor()


    # get a list of entries without full text
    xSQL_entries = '''SELECT 
                        xrecord_uid,
                        xrss_channel,
                        xfeed_entry_url
                     FROM
                      res_news_feeds
                     where xfeed_entry_fulltext is null
                     and xrss_channel 
                     not in ('sciencedaily', 'nytimes', 'economist', 'cen', 'lemonde',
                     'biology_news')
                     --limit 10
                    '''



    xdf_entries = pd.read_sql(xSQL_entries, xDBCon_pd)
    print 'records to be retrieved:', len(xdf_entries)


    # For Update later
    xSQL_Stm = """UPDATE res_news_feeds SET xfeed_entry_fulltext = ? WHERE xfeed_entry_url = ?"""

    xGroups = xdf_entries.groupby('xrss_channel')

    for xGroup in xdf_entries.groupby('xrss_channel'):

        xDF_Group = (xGroup[1]).drop_duplicates()
        print 'processing:', xGroup[0], 'records:', len(xDF_Group)
        xlst_tpls = zip(xDF_Group.xrecord_uid, xDF_Group.xfeed_entry_url)
        # we get the full text
        try:
            xlst_DataFullText = selenium_get_urls(xlst_tpls)

            # Inserting the full text in the database

            for xEntryData in xlst_DataFullText:
                xDataTuples = (xEntryData['xFullText'], xEntryData['xUrl'])
                xCursor.execute(xSQL_Stm, xDataTuples)

            xDBCon.commit()
        except:
            xDBCon.commit()
            print '--!error! --'

        print '---- update completed !'

    # Close the Database
    xDBCon.close()

    print 'fetching fulltext completed !'


def res_news_feeds_dois():
    '''
    get the dois from fulltext
    '''

    '''--- 3. GET dois from fulltext ---- '''

    # connection using sqlite3 (for inserts)
    xDBCon = sqLite.connect(xDB)
    xCursor = xDBCon.cursor()

    # get records for which dois need to be extracted

    xSQL_Stm = '''select 
                    xrecord_uid,
                    xfeed_entry_url,
                    xfeed_entry_fulltext
                  from 
                   res_news_feeds
                  where  
                   xfeed_entry_fulltext is not null 
                  and 
                   xfeed_entry_dois is null 
    '''
    xdf = pd.read_sql(xSQL_Stm, xDBCon_pd)
    print 'records retrieved:', len(xdf)

    # SQL for Updating
    xSQL_Stm = """UPDATE res_news_feeds SET xfeed_entry_dois = ? WHERE xfeed_entry_url = ?"""

    for xRow in xdf.iterrows():
        xData = dict(xRow[1])

        xDOI_lst = get_doi(xData['xfeed_entry_fulltext'])
        if len(xDOI_lst):
            xDOI_lst_Str = ';'.join(xDOI_lst)
            # print xData['xrecord_uid'], '---',   xDOI_lst_Str
            xDataTuples = (xDOI_lst_Str, xData['xfeed_entry_url'])
            # print xDataTuples
            xCursor.execute(xSQL_Stm, xDataTuples)

    xDBCon.commit()

    # Close the Database
    xDBCon.close()

    print 'all dois retrieved from fulltext'


def res_news_feeds_dois_link():
    '''
     update table linking news feed to dois
    '''


    '''--- 4. update table linking news feed to dois  ---- '''
    # connection using sqlite3 (for inserts)
    xDBCon = sqLite.connect(xDB)
    xCursor = xDBCon.cursor()

    # data to insert in the table taken from the res_news_feeds
    xSQL_Stm = '''select 
                   xrecord_uid,
                   xfeed_entry_url,
                   xfeed_entry_dois
                  from 
                   res_news_feeds
                   where xfeed_entry_dois is not null 
                   and xrecord_uid not in (select distinct xrecord_uid from res_news_feeds_doi)
                   --limit 10
               '''
    xdf = pd.read_sql(xSQL_Stm, xDBCon_pd)
    print 'record retrieved res_news_feeds_doi ', len(xdf)

    for xRow in xdf.iterrows():
        xData = dict(xRow[1])
        # print xData['xfeed_entry_dois']
        xLst_DOIs = (xData['xfeed_entry_dois']).split(';')
        for xDOI in xLst_DOIs:
            xDictData = dict.fromkeys(['xrecord_uid', 'xfeed_entry_url', 'xfeed_entry_doi'])
            xDictData['xrecord_uid'] = xData['xrecord_uid']
            xDictData['xfeed_entry_url'] = xData['xfeed_entry_url']
            xDictData['xfeed_entry_doi'] = xDOI

            xcolumns = ', '.join(xDictData.keys())
            xplaceholders = ':' + ', :'.join(xDictData.keys())
            xquery = 'INSERT INTO res_news_feeds_doi (%s) VALUES (%s)' % (xcolumns, xplaceholders)
            # print xquery
            xCursor.execute(xquery, xDictData)
            xDBCon.commit()

    xDBCon.close()

    print 'all entries for res_news_feeds_doi recorded !!'


    ''' !!!! TO DO :  UPDATE THE PUBLICATION RECORDS USING NEW DOIs retrieved'''



