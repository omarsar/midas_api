import pymongo
from pymongo import MongoClient
import operator
import json
import numpy as np
import bisect
import random
from time import sleep
from idCrawler import *



def writeUsers(tweets, collectionName = "regularUser_en_fixed"):
	collection = MongoClient("localhost", 27017)["idea"][collectionName]
	collection.insert(tweets)
	print("{} tweets inserted".format(len(tweets)))


BPD_users = json.load("BDP_candidates.json")

i =0
tweets = []
for screen_name in BPD_users[i:]:
	i += 1
	tweets += getTweets(screen_name = screen_name)
	print("trial {}".format(i))


