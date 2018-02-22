
'''
update records
'''






from src_update_news_feeds import  res_news_feeds_fetch
from src_update_news_feeds import  res_news_feeds_getfulltext
from src_update_news_feeds import res_news_feeds_dois
from src_update_news_feeds import res_news_feeds_dois_link


from src_update_funding_agencies import res_pub_funder_monitor

from src_update_crossref_pub import res_pub_crossref_update
from src_update_crossref_pub import res_pub_crossref_insert_records
from src_update_crossref_pub import res_pub_crossref_insert_records_highlights

from src_update_altmetrics import res_pub_altmetrics_update
from src_update_altmetrics import res_pub_altmetrics_text_news
from src_update_altmetrics import res_pub_altmetrics_news_links
from src_update_altmetrics import res_pub_altmetrics_news_links_resolve

#-- validating the funding info from crossref

from src_validate_crossref_funding_info import crossref_funding_ids_retrieve



xDB = '/media/SSD_960/___DATA_STAGING/_research_spotlight/research_spotlight.db'
xDBCon_pd = 'sqlite:///' + xDB  # Connection to use with pandas (for quick reading)




#'''--------------------------------'''
print '!!--updating the news feeds'
#'''--------------------------------'''

res_news_feeds_fetch()
res_news_feeds_getfulltext()
res_news_feeds_dois()
res_news_feeds_dois_link()


'''----------------------------------------------'''
print '!!--updating pubs from funding agencies'
'''-----------------------------------------------'''
res_pub_funder_monitor()


# !!! before updating : add records from other tables
res_pub_crossref_insert_records_highlights()


'''----------------------------------------------'''
print '!!--updating pub records '
'''-----------------------------------------------'''

# updating
res_pub_crossref_update()



'''----------------------------------------------'''
print '!!--processing altmetrics '
'''-----------------------------------------------'''

res_pub_altmetrics_update()

res_pub_altmetrics_text_news()


#-- update the table with news links

res_pub_altmetrics_news_links()

# -- resolve the links
# !!! does not work for some, notaby PhysOrg, consider also when status code is 400
#
res_pub_altmetrics_news_links_resolve()
## -


'''----------------------------------------
print  VALIDATING FUNDING INFORMATION FROM CROSSREF
----------------------------------------------'''

crossref_funding_ids_retrieve()



print '------ ALL ALL DONE '