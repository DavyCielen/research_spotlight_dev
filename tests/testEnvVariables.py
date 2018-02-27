import nose
import pymysql
import pandas as pd
import os

# make sure you have copied the file with environmental variables into the directory and run the docker

def testEnvVariables2():
    """check that the environmental variables are set"""
    """if these tests fail, make sure you have copied the envVars.env file,
    this contains passswords and is stored outside the gitRepo"""
    assert os.environ["ERC_MYSQL_RESEARCH_HIGHLIGHTS_PASSWORD"]
    assert os.environ["ERC_MYSQL_RESEARCH_HIGHLIGHTS_DATABASE"]
    assert os.environ["ERC_MYSQL_RESEARCH_HIGHLIGHTS_USER"]
    assert os.environ["ERC_MYSQL_RESEARCH_HIGHLIGHTS_LINK"]

def testMySQLConnection():
    xUsername = os.environ["ERC_MYSQL_RESEARCH_HIGHLIGHTS_USER"]
    xPassword = os.environ["ERC_MYSQL_RESEARCH_HIGHLIGHTS_PASSWORD"]
    xDatabase = os.environ["ERC_MYSQL_RESEARCH_HIGHLIGHTS_DATABASE"]
    xHost = os.environ["ERC_MYSQL_RESEARCH_HIGHLIGHTS_LINK"]
    connection = pymysql.connect(user=xUsername,
                                 password=xPassword,
                                 database=xDatabase,
                                 host=xHost)
    assert pd.read_sql("select 1 as x", connection)["x"][0] == 1
