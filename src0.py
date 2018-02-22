#!/usr/bin/env python2
#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 27 21:24:04 2018

@author: mike

-- colleaction of functions needed research_spotlight

"""

"""
--- CROSSREF ----
[1]. get data 
[2]. parse_metadata
[3]. parse_funding 
[4]. parse_affiliations 

"""
import datetime
import uuid
from crossref.restful import Works, Etiquette
import feedparser

import time
from selenium import webdriver
import random

import re

import requests
import json
from bs4 import BeautifulSoup
import pandas as pd



# my_etiquette = Etiquette('My Project Name', 'My Project version', 'My Project URL', 'My contact email')
xEtiquette = Etiquette(application_name='not yet set',
                       application_version='not yet set',
                       application_url='not yet public',
                       contact_email='almugabo@gmail.com')

x_works = Works(etiquette=xEtiquette)


def crossref_get_records_bydoi(xDOIStr):
    '''
    get data on a given article with a doi
    # LATER : TO DO
    # ADD AFFILIATION INFO, WHERE WE HAVE IT
    '''

    xDOI_Data = x_works.doi(xDOIStr)

    # ---- Results:
    # article metadata

    xResDict_art = dict.fromkeys(['pub_doi', 'pub_crossref_raw'])

    xResDict_art['pub_doi'] = xDOI_Data['DOI']
    xResDict_art['pub_crossref_raw'] = str(xDOI_Data)

    return xResDict_art


def crossref_get_records_byfunder(xfunder_doi, x_last_update):
    '''
    to get publications records from crossref
    given funder_doi and last update date

    TO DO : possibly give two possible dates
    '''
    xRes_lst = []

    xIter_pub_records = x_works.filter(from_pub_date=x_last_update,
                                       funder=xfunder_doi)

    for x_pub_record in xIter_pub_records:
        xDictData = dict.fromkeys(['record_uid', 'record_timestamp', 'pub_record_doi', 'pub_record_crossref_raw'])
        xDictData['record_uid'] = str(uuid.uuid4())
        xDictData['record_timestamp'] = str(datetime.datetime.now())
        xDictData['pub_record_doi'] = x_pub_record['DOI']
        xDictData['pub_record_crossref_raw'] = str(x_pub_record)
        xRes_lst.append(xDictData)
    return xRes_lst


def crossref_parse_metadata(x_crossrefpub_json):
    '''
    to parse crossref records and extract metadata
    '''

    xResDict_art = dict.fromkeys(
        ['art_doi', 'art_type', 'art_authors', 'art_pubyear', 'art_title', 'art_journal', 'art_bibref'])

    # --- get article metadata
    xDOI_Data = x_crossrefpub_json

    xDOI = xDOI_Data['DOI']
    xArticleType = xDOI_Data['type']

    if xDOI_Data.has_key('author'):
        xAuthors = xDOI_Data['author'][0]['family'] + ', ' + xDOI_Data['author'][0]['given'][0]
        if len(xDOI_Data['author']) > 1:
            xAuthors = xAuthors + ' et al.'
    else:
        xAuthors = ''

    if xDOI_Data.has_key('created'):
        xYear = xDOI_Data['created']['date-parts'][0][0]
    else:
        xYear = ''

    if xDOI_Data.has_key('title'):
        xTitle = xDOI_Data['title'][0]
    else:
        xTitle = ''

    if xDOI_Data.has_key('title'):
        xJournal = xDOI_Data['container-title'][0]
    else:
        xJournal = ''

    xMetaBibReference = xAuthors + '(' + str(xYear) + '). ' + xTitle + '. ' + xJournal + ' ' + xDOI

    xResDict_art['art_doi'] = xDOI
    xResDict_art['art_type'] = xArticleType
    xResDict_art['art_authors'] = xAuthors
    xResDict_art['art_pubyear'] = xYear
    xResDict_art['art_title'] = xTitle
    xResDict_art['art_journal'] = xJournal
    xResDict_art['art_bibref'] = xMetaBibReference

    return xResDict_art


def crossref_parse_funding(x_crossrefpub_json):
    '''
    to parse crossref records and extract metadata
    '''
    # funding information
    xResList_funding = []

    # --- get article metadata
    xDOI_Data = x_crossrefpub_json
    xDOI = xDOI_Data['DOI']

    # --- funding info (N.B: not always availaible )

    if xDOI_Data.has_key('funder'):
        xData_Funders = xDOI_Data['funder']
        for xFunder in xData_Funders:
            xDictData = dict.fromkeys(['art_doi', 'funder_doi', 'funder_name', 'funder_grants'])
            xDictData['art_doi'] = xDOI
            if xFunder.has_key('DOI'):
                xDictData['funder_doi'] = xFunder['DOI']
            if xFunder.has_key('name'):
                xDictData['funder_name'] = xFunder['name']
            if xFunder.has_key('award'):
                xDictData['funder_grants'] = ';'.join(xFunder['award'])
            xResList_funding.append(xDictData)

    return xResList_funding


def rss_get_feeds(rss_channel, rss_url):
    '''
    get and parse Feeds from a given channel and url
    return:
    - a list of feed.entries
    a list of feeds
    '''
    xlst_fields = ['xrecord_uid',
                   'xrss_channel',
                   'xrss_url',
                   'xfeed_timestamp',
                   'xfeed_entry_id',
                   'xfeed_entry_url',
                   'xfeed_entry_title',
                   'xfeed_entry_summary',
                   'xfeed_entry_published',
                   'xfeed_entry_raw']

    xfeed_records = feedparser.parse(rss_url)

    xlstres_feed_entries = []

    for xfeed_entry in xfeed_records.entries:

        xfeed_entry_data_dict = dict.fromkeys(xlst_fields)

        xfeed_entry_data_dict['xrecord_uid'] = str(uuid.uuid4())

        xfeed_entry_data_dict['xrss_channel'] = rss_channel
        xfeed_entry_data_dict['xrss_url'] = rss_url
        xfeed_entry_data_dict['xfeed_timestamp'] = str(datetime.datetime.now())

        if xfeed_entry.has_key('id'):
            x_id = xfeed_entry['id']
        else:
            x_id = xfeed_entry['link']

        xfeed_entry_data_dict['xfeed_entry_id'] = x_id
        xfeed_entry_data_dict['xfeed_entry_url'] = xfeed_entry['link']
        xfeed_entry_data_dict['xfeed_entry_title'] = xfeed_entry['title']
        xfeed_entry_data_dict['xfeed_entry_summary'] = xfeed_entry['summary']

        xfeed_entry_data_dict['xfeed_entry_published'] = xfeed_entry['published']
        xfeed_entry_data_dict['xfeed_entry_raw'] = str(xfeed_entry)

        xlstres_feed_entries.append(xfeed_entry_data_dict)

    return xlstres_feed_entries


'''
# ---- SELENIUM 
'''


# !pip install selenium
# install chromium web browser
# sudo apt update
# Install chromium.
# sudo apt install chromium-browser
# install chromedriver
# sudo apt-get install chromium-chromedriver

# https://askubuntu.com/questions/539498/where-does-chromedriver-install-to


# TO disable the notifications about controlled by automated process
# http://support.applitools.com/customer/en/portal/articles/2783976-%22chrome-is-being-controlled-by-automated-test-software%22-notification



def selenium_get_urls(xListTuplesUrls,
                      xPathChrome='/usr/lib/chromium-browser/chromedriver',
                      xTimes_Min=7,
                      xTimes_Max=23
                      ):
    '''
    given a list of tuples with ids and urls
    return a list of dictionaries with
    id, url and full text

    '''
    xTimes = range(xTimes_Min, xTimes_Max)

    # Result : a list of dictionaries with id and fulltext
    xlst_Res = []

    # add chrome options
    x_chrome_options = webdriver.ChromeOptions()
    x_chrome_options.add_argument("--disable-infobars")
    xdriver = webdriver.Chrome(executable_path=xPathChrome, chrome_options=x_chrome_options)
    xdriver.implicitly_wait(random.choice(xTimes))  # does not seem to work

    # get the urls
    for xUrl in xListTuplesUrls:
        xDictRes = dict.fromkeys(['xId', 'xUrl', 'xFullText'])
        xUrl_Fetch = xUrl[1]
        # print xUrl_Fetch
        xTime = random.choice(xTimes)
        xdriver.get(xUrl_Fetch)
        # wait some times
        time.sleep(xTime)


        xContent = xdriver.page_source  # .encode("utf8")

        xDictRes['xId'] = xUrl[0]
        xDictRes['xUrl'] = xUrl_Fetch
        xDictRes['xFullText'] = xContent

        xlst_Res.append(xDictRes)
    xdriver.quit()
    return xlst_Res


# get dois from a text



def get_doi(xText,
            xDOI_Expr='10\.\d{4,9}\/[-._;()/:A-Z0-9]+',
            xClean=True, xUnique=True):
    '''retrieve all dois from text
    #expression taken from here
    https://www.crossref.org/blog/dois-and-matching-regular-expressions/

    older expressions:
    was taking not only 10.xx but also 10000

    '10.\d{4,9}\/[-._;()/:A-Z0-9]+'

    '''

    def clean_doi(xStrDOI):
        '''
        some doi entries are terminated b
        by "." or ").".
        xStrDOI = '10.1126/sciadv.aao2623)'
        xStrDOI = '10.1126/sciadv.aao2623).'
        xStrDOI = '10.1111/jgs.15298/abstract'
        the function returm a clean doi string

        '''
        if xStrDOI[-2:] in [').']:
            xStrDOI = xStrDOI[:-2]
        if xStrDOI[-1:] in [')', '.']:
            xStrDOI = xStrDOI[:-1]
        if xStrDOI.endswith('/abstract'):
            xStrDOI = xStrDOI[:-9]
        if xStrDOI.endswith('/full'):
            xStrDOI = xStrDOI[:-5]
        return xStrDOI

    # return doi matches with regular expressions
    xlst_Res = re.findall(xDOI_Expr, xText, flags=re.IGNORECASE)

    if xClean:
        xlst_Res = [clean_doi(x) for x in xlst_Res]
    if xUnique:
        xlst_Res = list(set(xlst_Res))

    return xlst_Res


'''
--------------------------------------------------------------
ALTMETRICS 
--------------------------------------------------------------
'''


def altmetrics_get_by_doi(x_doi):
    '''
    to fetch data from altmerics in raw format
    for processing later
    '''
    xUrlBase = 'https://api.altmetric.com/v1/doi/'
    xUrlToFetch = xUrlBase + x_doi
    xq1 = requests.get(xUrlToFetch)

    if xq1.status_code == 200:
        xData_altmetrics = json.loads(xq1.content)
        xData_altmetrics_raw = str(xData_altmetrics)
    else:
        xData_altmetrics_raw = 'ERROR !!!' + str(xq1.status_code)

    return xData_altmetrics_raw


def altmetrics_parse_data(xDataAltmetrics_Json):
    '''
    parse altmetrics response json and extract data of interest

    N.B:

    if it is a stringified json, it can can be changed with
    ast.literal_eval(xRec)
    '''
    xlst_fields = ['altmetric_id',
                   'altmetric_url',
                   'cnt_blogs',
                   'cnt_news_outlet',
                   'cnt_policy_docs',
                   'cnt_mendeley',
                   'cnt_twitters', 'cnt_fbook',

                   'cnt_total_post', 'cnt_total_accounts']

    xRecData = xDataAltmetrics_Json
    xDataDict = dict.fromkeys(xlst_fields)

    xDataDict['altmetric_id'] = xRecData['altmetric_id']

    xDataDict['altmetric_url'] = 'https://www.altmetric.com/details/' + str(xRecData['altmetric_id'])

    if xRecData.has_key('cited_by_feeds_count'):
        xDataDict['cnt_blogs'] = xRecData['cited_by_feeds_count']
    if xRecData.has_key('cited_by_msm_count'):
        xDataDict['cnt_news_outlet'] = xRecData['cited_by_msm_count']

    if xRecData.has_key('cited_by_policies_count'):
        xDataDict['cnt_policy_docs'] = xRecData['cited_by_policies_count']
    if xRecData.has_key('readers'):
        if xRecData['readers'].has_key('mendeley'):
            xDataDict['cnt_mendeley'] = xRecData['readers']['mendeley']

    if xRecData.has_key('cited_by_tweeters_count'):
        xDataDict['cnt_twitters'] = xRecData['cited_by_tweeters_count']
    if xRecData.has_key('cited_by_fbwalls_count'):
        xDataDict['cnt_fbook'] = xRecData['cited_by_fbwalls_count']
    if xRecData.has_key('cited_by_posts_count'):
        xDataDict['cnt_total_post'] = xRecData['cited_by_posts_count']
    if xRecData.has_key('cited_by_accounts_count'):
        xDataDict['cnt_total_accounts'] = xRecData['cited_by_accounts_count']

    return xDataDict


def altmetrics_parse_news(x_altmetrics_text_news):
    '''
    parse a text from altmetrics news
    returns a list of postings with title, summary, link etc ...
    '''
    xlstRes = []
    xsoup = BeautifulSoup(x_altmetrics_text_news, 'html.parser')
    xlst_posts_news = xsoup.findAll('article', {'class': 'post msm'})

    for xpost_news in xlst_posts_news:
        xDictData = dict.fromkeys(['post_link', 'post_title', 'post_source', 'post_time', 'post_summary'])
        # url_link
        try:
            xDictData['post_link'] = xpost_news.find("a", {"class": "block_link"})['href']
        except:
            pass
        # title
        try:
            xDictData['post_title'] = xpost_news.find('div', {'class': 'content with_image'}).find('h3').text
        except:
            pass
            # source and date
        try:
            x_post_source_time = xpost_news.find('div', {'class': 'content with_image'}).find('h4').text
            x_post_source_time_lst = x_post_source_time.split(',')

            xDictData['post_source'] = x_post_source_time_lst[0]
            xDictData['post_time'] = x_post_source_time_lst[1]
        except:
            pass

        # summary
        try:
            xDictData['post_summary'] = xpost_news.find('p', {'class': 'summary'}).text
        except:
            pass

        xlstRes.append(xDictData)

    return xlstRes



'''
--------------------------------------------------------------
--- UTILITIES  
--------------------------------------------------------------
'''


def util_DFrame_InsertBlankRow(xDF, xGroupingVariable):
    ''' creates a new Dataframe with empty rows
    between groups
    useful for example for visual inspection of duplicates
    in excel etc ...
    Input :
    - DataFrame
    - Grouping Variables
    Usage:
    d = {'City' : ['a', 'a', 'a', 'b', 'b', 'c'],
      'Museum' :['A1', 'A2', 'A3', 'B1', 'B2', 'C1'],
      'Visitors': [10, 30, 20, 40, 100, 0]}
    df = pd.DataFrame(d)
    DFINSERTEMPTYROW(df, 'City')
    '''
    # Create an Empty DataFrame
    xListColumns = list(xDF.columns)
    xEmptyDF = pd.DataFrame(dict(zip(xListColumns, [[''] for x in xListColumns])))
    # Create a new DataFrame with empty rows between the groups
    xDFNew = pd.DataFrame(columns=xListColumns)
    # Create Groups
    xGroups = xDF.groupby(xGroupingVariable)
    # Loop Through the groups and add empty row
    for x in xGroups:
        xDFNew = xDFNew.append(pd.DataFrame(dict(x[1])))
        xDFNew = xDFNew.append(xEmptyDF)

    return xDFNew



