import dataset
from enum import Enum
import requests as rq
from bs4 import BeautifulSoup


'''test logic without actually downloading'''


class store():
    db = dataset.connect("sqlite:///test.db")

class journalMixin():
    def download_journal_main_page(self,url):
        page = rq.get(url).content
        return page #if success

class Nature(journalMixin):
    def __init__(self):
            self.base_url = "http://nature.com"

    def download_main_page(self):
            postfix = "-".join([str(x) for x in range(2010,2050)]) # change to current year end
            uri = self.base_url  + "/nature/archive/index.html?year=%s" % postfix
            page = rq.get(uri)
            self.archive_content = page.content
            soup = BeautifulSoup(page.content,"lxml")
            return [self.base_url + link["href"] for link in soup.find_all("a") if "/nature/journal/" in link["href"]]


class Science(journalMixin):

    def download_main_page(self):
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

source().update("nature")
source().updateTodos()
