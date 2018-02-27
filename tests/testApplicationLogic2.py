import itertools
import dataset
from enum import Enum
import requests as rq
from bs4 import BeautifulSoup
import pandas as pd

'''test logic without actually downloading'''


class store():
    db = dataset.connect("sqlite:///test.db")

class journalMixin():
    def download_journal_main_page(self,url):
        ''' specific volume'''
        page = rq.get(url).content
        return page #if success

class Nature(journalMixin):
    def __init__(self):
            self.base_url = "http://nature.com"

    def download_main_page(self):
            '''page that lists all the issues'''
            postfix = "-".join([str(x) for x in range(2010,2050)]) # change to current year end
            uri = self.base_url  + "/nature/archive/index.html?year=%s" % postfix
            page = rq.get(uri)
            self.archive_content = page.content
            soup = BeautifulSoup(page.content,"lxml")
            return [self.base_url + link["href"] for link in soup.find_all("a") if "/nature/journal/" in link["href"]]

    def extract_doi_for_issue(self, HTML):
        #nature has a new ui which is encoded here, the old one not yet
        soup = BeautifulSoup(HTML,'lxml')
        rhighlts_div = soup.find("div",{"id":"rhighlts"})
        #articles = [[y.find("a")["href"] for y in x.find_all("article")] for x in rhighlts_div if x != None]
        #new_ui = [y for y in articles if len(y)==1]
        #new_ui_downloads = [[rq.get("http://nature.com" + y) for y in x] for x in new_ui]
        #soups = [[BeautifulSoup(p.content,'lxml') for p in x] for x in new_ui_downloads]
        #find all articles in page
        #articles = y.find_all("article")
        #soup_doi_links = [[y.find_all("a",{"data-track-label":"original research"}) for y in x] for x in soups]
        #soup_title_links = [[y.find_all("a",{"data-track-label":"title"}) for y in x] for x in soups]
        #soup_doi_links_flat = list(itertools.chain(*soup_doi_links))
        #soup_title_links_flat = list(itertools.chain(*soup_title_links))
        #soup_title_hrefs = [x["href"] for x in soup_title_links_flat[0]]
        #soup_doi_hrefs= [x["href"] for x in soup_doi_links_flat[0]]
        #new_ui_df = pd.DataFrame({"pub_id":soup_doi_hrefs,"highlight_link":soup_title_hrefs})
        #print(soup_doi_hrefs)
        #print(len(soup_doi_hrefs))
        #print(len(soup_title_hrefs))

class Science(journalMixin):

    def download_main_page(self):
        '''page that lists all the issues'''
        '''returns a list of all entries on page'''
        return ["link science 1","link science 2"]


class updateStatus(Enum):
    TODO = "todo"
    FAIL = "fail"
    SUCCESS = "success"
    IGNORE = "ignore"


class source(store):
    sources = {
           'nature':Nature(),
           'science':Science()
          }

    def __init__(self):
        self.source_table = self.db['source']

    def updateTodos(self,source = None):
        pagesTodo = self.source_table.find(status=updateStatus.TODO.value)
        for page in pagesTodo:
            self.download_journal_main_page(source=page["sourceType"],url = page["url"])

    def download_journal_main_page(self,source = None, url=None):
        pageHTML = self.sources[source].download_journal_main_page(url)
        if pageHTML:
            self.source_table.update({"url":url,
                                      "status": updateStatus.SUCCESS.value,
                                      "pageHTML":pageHTML},
                                      "url")
        else:
            self.source_table.update({"url":url,
                                      "status": updateStatus.FAIL.value},
                                      "url")

    def parse_journal_main_page(self, source=None):
        observation = self.source_table.find_one()
        HTML = observation["pageHTML"]
        self.sources[source].extract_doi_for_issue(HTML)
        #print(observation)

    def update(self, source = None):
        '''delete'''
        toParse = True
        '''find all links and upsert if not exist'''
        pages = self.sources[source].download_main_page()
        '''download if in criteria'''
        for page in pages:
            self.source_table.upsert({"url":page, "sourceType":source},"url")
        '''find new pages and set status to either todo or ignore'''
        newPages = self.source_table.find(status=None)
        for page in newPages:
            if toParse:
                self.source_table.update({"url":page["url"], "status":updateStatus.TODO.value},"url")
            else:
                self.source_table.update({"url":page["url"], "status":updateStatus.IGNORE.value},"url")

source().parse_journal_main_page("nature")
