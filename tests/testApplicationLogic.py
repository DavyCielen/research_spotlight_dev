import dataset
from enum import Enum

'''test logic without actually downloading'''


class store():
    db = dataset.connect("sqlite:///test.db")

class Nature():

    def download_main_page(self):
        return ["link nature 1","link nature 2"]
    def download_journal_main_page(self,url):
        page = '''<html><body>nature page</body></html>'''
        return page #if success

class Science(store):

    def download_main_page(self):
        '''returns a list of all entries on page'''
        return ["link science 1","link science 2"]
    def download_journal_main_page(self,url):
        page = '''<html><body>nature page</body></html>'''
        return page #if success

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
