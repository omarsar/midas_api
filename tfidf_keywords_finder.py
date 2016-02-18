import math
from textblob import TextBlob as tb
from pymongo import MongoClient

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



randomBlob = tb(randomTweets)
BDPBlob = tb(BDPTweets)


bloblist = [randomBlob, BDPBlob]




for i, blob in enumerate(bloblist):
    print("Top words in document {}".format(i + 1))
    scores = {word: tfidf(word, blob, bloblist) for word in blob.words}
    sorted_words = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    for word, score in sorted_words[:20]:
        print("\tWord: {}, TF-IDF: {}".format(word, round(score, 5)))
