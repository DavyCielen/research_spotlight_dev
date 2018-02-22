/*
structure of the db tables
- we start with sqlite
- later migrate to Google BigQuery

/home/mike/PycharmProjects/

*/

--db name / table space / research_spotlight

-- res_pub_crossref
-- res_pub_crossref_funding

-- res_news_source
-- res_news_feeds
-- res_news_feeds_doi

-- res_pub_highlights

-- res_pub_summaries

-- res_pub_altmetrics


------ possibly one can add datasets later such as
-- policy documents citing research paper
-- clinical trials citing research papers
-- patents citing research papers
-- also publications from other sources such as arxiv, bioarxiv etc ...
--etc ...



drop table if exists res_pub_crossref;

create table res_pub_crossref
(
record_uid               text,
record_timestamp         text,
pub_record_doi           text,
pub_record_crossref_raw  text,
pub_meta_authors         text,
pub_meta_pubyear         integer,
pub_meta_journal         text,
pub_meta_title           text,
pub_meta_bibref          text,
pub_meta_type            text
)
;

drop table if exists res_pub_crossref_funding;

create table res_pub_crossref_funding
(pub_doi text,
funder_doi      text,
funder_grants   text,
funder_name     text
);

alter table res_pub_crossref_funding add column grants_ids_validated text;
--update res_pub_crossref_funding set grants_ids_validated = NULL



-- research news feeds

drop table if exists res_news_feeds;

create table res_news_feeds
as
SELECT
t1.xrecord_uid,
t1.xrss_channel,
t1.xrss_url,
t1.xfeed_timestamp,
t1.xfeed_entry_id,
t1.xfeed_entry_url,
t1.xfeed_entry_title,
t1.xfeed_entry_summary,
t1.xfeed_entry_published,
t1.xfeed_entry_raw,
t1.xfeed_entry_fulltext,
t1.xfeed_entry_dois
FROM
rss_feed_entries AS t1
--LIMIT 10
;

drop table if exists res_news_feeds_doi;

create table res_news_feeds_doi
(xrecord_uid      text,
xfeed_entry_url   text,
xfeed_entry_doi   text
)
;


-- altmetrics

drop table if exists res_pub_altmetrics;

create table res_pub_altmetrics
(
xpub_doi       text,
altmetric_raw  text,
altmetric_id   integer,
altmetric_url  text,
cnt_blogs         integer,
cnt_fbook         integer,
cnt_mendeley      integer,
cnt_news_outlet   integer,
cnt_policy_docs   integer,
cnt_twitters       integer,
cnt_total_accounts integer,
cnt_total_post     integer
)
;

-- to add text of news outlet

alter table res_pub_altmetrics add column text_news_outlet text;



INSERT INTO destinationTable (risposta, data_ins)
SELECT STATUS risposta, DATETIME('now') data_ins
FROM   sourceTable




-- UPDATES DATE

drop table if exists _last_update;
create table _last_update
(lstupd_crossref_funder text,
 lstupd_altmetrics text,
 lstupd_res_news_feeds text
)
;

insert into _last_update (lstupd_crossref_funder) VALUES ('2018-01-25');



-- ALTMETRICS NEWS_POSTS

drop table if exists res_pub_altmetrics_news;

create table  res_pub_altmetrics_news
(
xpub_doi       text,
altmetric_url  text,
post_link      text,
post_title     text,
post_source    text,
post_time      text,
post_summary       text,
post_link_resolved text
)
;









--- FUNDERS TO MONITOR

drop table if exists res_pub_funder_monitor;

create table res_pub_funder_monitor
(funder_doi text,
 funder_name text
);

insert into
res_pub_funder_monitor (funder_doi, funder_name)
VALUES ('10.13039/100011199', 'FP7 Ideas: European Research Council');

insert into
res_pub_funder_monitor (funder_doi, funder_name)
VALUES ('10.13039/100010663', 'H2020 European Research Council');

insert into
res_pub_funder_monitor (funder_doi, funder_name)
VALUES ('10.13039/501100000781', 'European Research Council');


-- newsfeeds sources

insert into
res_news_source (record_id , rss_channel, rss_url)
VALUES (34, 'biology_news', 'http://feeds.biologynews.net/biologynews/headlines');

-- to insert
insert into
res_news_source (record_id , rss_channel, rss_url)
VALUES (35, 'innovations_ report', 'http://www.innovations-report.com/rss.xml');


/*
TABLE GRANT DATASET
*/


-- should be taken from the grant_db once completed

drop table if exists _res_spotlight_grants;

create table _res_spotlight_grants
as
SELECT
t1.prop_id_a1 AS proj_id,
t1.call_a1 AS proj_call,
t1.prop_title AS proj_title,
t1.cda_completedflagyn AS proj_status,
t1.cda_pifirstname AS pi_name_first,
t1.cda_pilastname AS pi_name_last,
t1.cda_pisex AS pi_gender,
t1.cda_name_clean  as pi_org_name,
t1.cda_country_legal as pi_org_country
FROM
core_datasets.x_rep_master_basic AS t1
WHERE
t1.a1_propstatus_funded = 'Y'
and t1.callschema_a1 not in ('5_PoC')
--limit 10
;










