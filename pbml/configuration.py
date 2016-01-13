#!/usr/bin/env python

import json


def loadConfig(file):
    """docstring for loadConfig"""
    
    try:
        with open(file, 'r') as file:
            return json.loads(' '.join([line for line in file]))
    except:
        print "Filed to locate a config file for the repo"
        raise
    