#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import Enum
import json

# pip install dnspython
from dns.rdatatype import NULL

# pip install pymongo
from pymongo import MongoClient
from gridfs import GridFSBucket
from bson.json_util import dumps
import copy
import os, sys
import datetime

# pip install pyyaml
import yaml

class MissionStatus(Enum):
    RUNNING = 0
    SUCCEEDED = 1
    PAUSED = 2
    ERROR = 3
    CANCEL = 4

# "mongodb://coffee:coffee@localhost:27017"
class MongodbStorage:
    def __init__(self, connectionString="mongodb://localhost:27017/"):
        self.client = MongoClient(connectionString)
        self.database = self.getDatabase("admin")
        self.lichsuCollection = self.database["lich_su"]
        self.vanhocCollection = self.database["van_hoc"]
    # Save data need update
        self.fs = GridFSBucket(self.database)

    def getDatabase(self, args):
        return self.client[args]

    def printJson(self, data):
        print(dumps(data, indent=4, sort_keys=True))
        return data

    def bson2Json(self, data):
        return dumps(data, indent=4, sort_keys=True)

    def bson2Dict(self, data):
        json.loads(self.bson2Json(data))

    def load_cau_hoi(self, linh_vuc, number):
        """Load data from mongodb

        Args:
            fileName (String): name of file in mongodb
        Return:
            data (dict): data result
        """
        if linh_vuc == "van_hoc":

            data = self.vanhocCollection.find_one({"STT": number})
        if "Câu hỏi" not in data:
            print("No have this data in database")
            return None
        else:
            print("Load data in database done")
            return data