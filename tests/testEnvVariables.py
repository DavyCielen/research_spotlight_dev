import nose

import os

# make sure you have copied the file with environmental variables into the directory and run the docker

LOCAL_INSTALL_DIR_ENV_FILES = os.path.join(os.getcwd() ,"config","envVars.env")


def testEnvVariables2():
    """check that the environmental variables are set"""
    assert os.environ["ERC_MYSQL_RESEARCH_HIGHLIGHTS_PASSWORD"]
    assert os.environ["ERC_MYSQL_RESEARCH_HIGHLIGHTS_DATABASE"]
    assert os.environ["ERC_MYSQL_RESEARCH_HIGHLIGHTS_USER"]
    assert os.environ["ERC_MYSQL_RESEARCH_HIGHLIGHTS_LINK"]
