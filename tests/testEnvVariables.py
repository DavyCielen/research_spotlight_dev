import nose

import os

# make sure you have copied the file with environmental variables into the directory and run the docker


def testEnvVariables():
    assert(os.environ['testEnvVarsExists']) != None)
