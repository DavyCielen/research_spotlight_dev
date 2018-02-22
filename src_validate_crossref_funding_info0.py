
'''
VALIDATING FUNDING INFORMATION COMING FROM CROSSREF
'''




import pandas as pd
import re
import sqlite3 as sqLite
# reg_expression to extract valid grant ids
xRefExp_GrantId = re.compile('\d{6}')

xDB = '/media/SSD_960/___DATA_STAGING/_research_spotlight/research_spotlight.db'
xDBCon_pd = 'sqlite:///' + xDB  # Connection to use with pandas (for quick reading)


def crossref_funding_ids_retrieve():
    '''
    retrieve valid grants ids from the entries in crossref


    :return:
    '''


    # get list of valid projects id
    xsql_sel = 'SELECT proj_id FROM _res_spotlight_grants '
    xdf_grants = pd.read_sql(xsql_sel, xDBCon_pd)
    xlst_grant_ids_valid = list(xdf_grants.proj_id)
    len(xlst_grant_ids_valid)

    # list of entries for which we need to extract the grant ids

    xsql_sel = '''select
                     distinct 
                    pub_doi, 
                    funder_grants,
                    funder_doi
                  from res_pub_crossref_funding
                  where funder_doi in (select distinct funder_doi from res_pub_funder_monitor)
                  and (length(trim(funder_grants) )> 2)
                  and grants_ids_validated is null 
                  --limit 50
                  '''
    xdf = pd.read_sql(xsql_sel, xDBCon_pd)
    print 'number of records in which to search the grants ids', len(xdf)

    # Update statememt
    xSQL_UpdateStm_meta = """UPDATE 
                             res_pub_crossref_funding
                             SET
                               grants_ids_validated = ?
                             WHERE 
                               pub_doi = ? 
                             AND 
                               funder_grants = ?  
                             AND 
                               funder_doi = ?
                      """

    # connection using sqlite3 (for inserts)
    xDBCon = sqLite.connect(xDB)
    xCursor = xDBCon.cursor()

    # update the entries

    for xRow in xdf.iterrows():
        xDictData = dict(xRow[1])
        xEntry_doi = xDictData['pub_doi']
        xEntry_grants = xDictData['funder_grants']
        xEntry_funder_doi = xDictData['funder_doi']

        xlst_Grants = xRefExp_GrantId.findall(xEntry_grants)
        # keep only those grants which are valid
        xlst_Grants = [x for x in xlst_Grants if x in xlst_grant_ids_valid]
        if len(xlst_Grants) > 0:
            xlst_Grants_Str = ';'.join(xlst_Grants)
        else:
            xlst_Grants_Str = '--no grant_id found --'

        xDataTuple = (xlst_Grants_Str, xEntry_doi, xEntry_grants, xEntry_funder_doi)
        xCursor.execute(xSQL_UpdateStm_meta, xDataTuple)

        xDBCon.commit()
    xDBCon.close()

    print 'all done'



''''
TO UPDATE MANUALLY 

select
    distinct 
    pub_doi, 
    funder_grants,
    funder_doi
from res_pub_crossref_funding
    where funder_doi in (select distinct funder_doi from res_pub_funder_monitor)
    and (length(trim(funder_grants) )> 2)
    and grants_ids_validated  = '--no grant_id found --'
order by  pub_doi

'''
