import math
from textblob import TextBlob as tb
from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
from gensim import corpora

def tf(word, blob):
    return blob.words.count(word) / len(blob.words)

def n_containing(word, bloblist):
    return sum(1 for blob in bloblist if word in blob)

def idf(word, bloblist):
    return math.log(len(bloblist) / (1 + n_containing(word, bloblist)))

def tfidf(word, blob, bloblist):
    return tf(word, blob) * idf(word, bloblist)

def load_stopwords(file_location="SmartStoplist"):
	f = open(file_location)
	return [line.strip() for line in f]
	



stopwords = load_stopwords()
client = MongoClient("localhost", 27017)
randomTweetsColl = client["idea"]["random-users"]
BDPTweetsColl = client["idea"]["BDP_tweets"]


randomTweets = ""
for tweet in randomTweetsColl.find():
	randomTweets += (tweet["text"] + "\n")





BDPTweets = ""
for tweet in BDPTweetsColl.find():
	BDPTweets += (tweet["text"] + "\n")


tfidf = TfidfVectorizer(stop_words = 'english', norm = 'l1')
x = tfidf.fit_transform([randomTweets,BDPTweets])