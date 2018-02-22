# coding: utf-8

# ## scripts to updata data

import pandas as pd
import sqlite3 as sqLite
import ast
import time
import random
import datetime
import requests



from src import selenium_get_urls


from src import altmetrics_get_by_doi
from src import altmetrics_parse_data
from src import altmetrics_parse_news

from fake_useragent import UserAgent


'''
**  SET PATH TO THE DATABASE 
'''
xDB = '/media/SSD_960/___DATA_STAGING/_research_spotlight/research_spotlight.db'
xDBCon_pd = 'sqlite:///' + xDB  # Connection to use with pandas (for quick reading)




'''
--------------------------------------------------------------
STEP 4 : UPDATE ALTMETRICS DATA 
---------------------------------------------------------------
'''

def res_pub_altmetrics_update():
    '''
    update records of the table publications records
    '''



    '''1. --- ADD ALTMETRICS data to the table -- in raw format ---- '''

    # get list of doi to process
    xSQL_lst_dois = '''select 
                         distinct pub_record_doi  
                        from 
                        res_pub_crossref
                        where
                        pub_record_doi  not in (select xpub_doi from res_pub_altmetrics)
                        '''
    xdf_1 = pd.read_sql(xSQL_lst_dois, xDBCon_pd)
    xlst_doi = list(xdf_1.pub_record_doi)
    print 'doi to process:', len(xlst_doi)

    # initalize db connection
    xDBCon = sqLite.connect(xDB)
    xCursor = xDBCon.cursor()

    xTimeWait = range(1, 3)

    for xDOI in xlst_doi:
        xDataDict = dict.fromkeys(['xpub_doi', 'altmetric_raw '])
        xRec = altmetrics_get_by_doi(xDOI)
        xDataDict['xpub_doi'] = xDOI
        xDataDict['altmetric_raw'] = xRec
        xTimeSleep = random.choice(xTimeWait)
        time.sleep(xTimeSleep)

        # insert
        xcolumns = ', '.join(xDataDict.keys())
        xplaceholders = ':' + ', :'.join(xDataDict.keys())
        xquery = 'INSERT INTO res_pub_altmetrics (%s) VALUES (%s)' % (xcolumns, xplaceholders)
        xCursor.execute(xquery, xDataDict)

        xDBCon.commit()

    # close db
    xDBCon.close()

    print 'altmetrics data added !'


    '''2. --- parse almetrics data  ---- '''

    xSQL_parse_altmetrics = '''select 
                                xpub_doi, 
                                altmetric_raw
                                from res_pub_altmetrics 
                                where altmetric_raw <>  "ERROR !!!404"
                                and altmetric_id is null 
                                '''
    xdf = pd.read_sql(xSQL_parse_altmetrics, xDBCon_pd)
    print 'almetrics to process ', len(xdf)

    # UPDATE STATEMENT
    xSQL_UpdateStm_meta = """UPDATE 
                             res_pub_altmetrics 
                             SET
                                altmetric_id     = ?,
                                altmetric_url    = ?,
                                cnt_blogs        = ?,
                                cnt_fbook        = ?,
                                cnt_mendeley     = ?,
                                cnt_news_outlet  = ?,
                                cnt_policy_docs  = ?,
                                cnt_twitters     = ?,
                                cnt_total_accounts  = ?,
                                cnt_total_post      = ?
                             WHERE 
                               xpub_doi = ? 
                      """

    # initalize db connection
    xDBCon = sqLite.connect(xDB)
    xCursor = xDBCon.cursor()

    # Parse dataframe and add data
    for xRow in xdf.iterrows():
        xDataDict = dict(xRow[1])
        x_doi = xDataDict['xpub_doi']
        x_altmetrics = ast.literal_eval(xDataDict['altmetric_raw'])
        x_altmetrics_data = altmetrics_parse_data(x_altmetrics)
        # we add doi for matching
        x_altmetrics_data['xpub_doi'] = x_doi

        xDataTuple = (x_altmetrics_data['altmetric_id'],
                      x_altmetrics_data['altmetric_url'],
                      x_altmetrics_data['cnt_blogs'],
                      x_altmetrics_data['cnt_fbook'],
                      x_altmetrics_data['cnt_mendeley'],
                      x_altmetrics_data['cnt_news_outlet'],
                      x_altmetrics_data['cnt_policy_docs'],
                      x_altmetrics_data['cnt_twitters'],
                      x_altmetrics_data['cnt_total_accounts'],
                      x_altmetrics_data['cnt_total_post'],

                      x_altmetrics_data['xpub_doi']
                      )
        # update
        xCursor.execute(xSQL_UpdateStm_meta, xDataTuple)

    xDBCon.commit()
    xDBCon.close()

    print 'parsed data from altmetrics added !!!'


def res_pub_altmetrics_text_news():
    '''
    get the text for the news for the entries where count news > 0
    '''

    # get data with news and which has not been processed

    xSQL_sel = '''SELECT
                    t1.xpub_doi,
                    t1.altmetric_url
                FROM
                    res_pub_altmetrics AS t1
                WHERE
                    t1.text_news_outlet IS null AND
                    t1.cnt_news_outlet > 0
                  --  limit 5
                '''

    xdf = pd.read_sql(xSQL_sel, xDBCon_pd)
    xdf.head()

    # list to fetch
    xlst_tup_urls = zip(xdf.xpub_doi, [x + '/news' for x in list(xdf.altmetric_url)])

    print 'altmetrics news texts to fetch:', len(xlst_tup_urls)

    # get the fulltext -- generous wait times

    xlst_DataFullText = selenium_get_urls(xListTuplesUrls=xlst_tup_urls,
                                          xTimes_Min=30,
                                          xTimes_Max=65)

    print 'all altmetrics news fetched:', len(xlst_DataFullText)

    # --- ADD THE TEXT TO THE DB

    # connection using sqlite3 (for update)
    xDBCon = sqLite.connect(xDB)
    xCursor = xDBCon.cursor()

    xSQL_update = """UPDATE res_pub_altmetrics SET text_news_outlet = ? WHERE xpub_doi = ?"""

    # xlst_DataFullTex[0]
    for xEntryData in xlst_DataFullText:
        xDataTuples = (xEntryData['xFullText'], xEntryData['xId'])
        xCursor.execute(xSQL_update, xDataTuples)
        # print 'added', xDataTuples[1]

        xDBCon.commit()
    xDBCon.close()
    print 'all altmetrics news text recorded !'


def res_pub_altmetrics_news_links():
    '''
    to update the table with table with altmetrcs news links
    '''

    # get the data not already parsed

    xsql = '''select 
              xpub_doi,
              altmetric_url, 
              text_news_outlet
              from res_pub_altmetrics 
              where text_news_outlet is not null
              and 
              xpub_doi not in (select distinct xpub_doi from res_pub_altmetrics_news)
              '''

    xdf = pd.read_sql(xsql, xDBCon_pd)

    len(xdf)

    # initalize db connection
    xDBCon = sqLite.connect(xDB)
    xCursor = xDBCon.cursor()

    for x1 in zip(list(xdf.xpub_doi), list(xdf.altmetric_url), list(xdf.text_news_outlet)):
        xDOI = x1[0]
        xAltmetric_Url = x1[1]
        xText = (x1[2]).encode('utf-8')

        xq1 = altmetrics_parse_news(xText)
        # we add doi and altmetrics url
        for xDict in xq1:
            xDict['xpub_doi'] = xDOI
            xDict['altmetric_url'] = xAltmetric_Url

            # insert the dictionary and commit
            xcolumns = ', '.join(xDict.keys())
            xplaceholders = ':' + ', :'.join(xDict.keys())
            xquery = 'INSERT INTO res_pub_altmetrics_news (%s) VALUES (%s)' % (xcolumns, xplaceholders)
            # print xquery
            xCursor.execute(xquery, xDict)
            xDBCon.commit()

    xDBCon.close()


    print 'altmetrics news updated !!!'


def res_pub_altmetrics_news_links_resolve():
    '''
    to resolve the links of the news.
    Most are given as ct.moreover
    '''

    xsql_sel = '''SELECT
                t1.xpub_doi,
                t1.altmetric_url, 
                t1.post_link
                FROM
                res_pub_altmetrics_news AS t1
                where t1.post_link is not null 
                --and t1.post_link_resolved is null 
                --and t1.post_source not in ('Phys.org')
                and t1.post_link_resolved = '!!error in url!!!'
                  '''

    xdf = pd.read_sql(xsql_sel, xDBCon_pd)

    print '--records to process : ', len(xdf)

    xSQL_UpdateStm = """UPDATE
                         res_pub_altmetrics_news
                        SET 
                         post_link_resolved = ?
                        WHERE 
                         post_link = ?
                     """
    # connection using sqlite3 (for inserts)
    xDBCon = sqLite.connect(xDB)
    xCursor = xDBCon.cursor()

    xTimes = range(1, 5)

    ua = UserAgent()
    header = {'User-Agent': str(ua.chrome)}

    for xpost_link in list(xdf.post_link):
        xTime_wait = random.choice(xTimes)
        time.sleep(xTime_wait)
        try:
            xq1 = requests.get(xpost_link, headers=header)

            if xq1.status_code in [200, 400]:
                xTupleData = (xq1.url, xpost_link)
            else:
                xTupleData = ('!!error in url!!!', xpost_link)
                print xq1.status_code

        except:
            xTupleData = ('!!error in url!!!', xpost_link)
            print 'error !!', xpost_link

        # update
        xCursor.execute(xSQL_UpdateStm, xTupleData)

        xDBCon.commit()
    xDBCon.close()

    print 'resolving of the links completed !'




