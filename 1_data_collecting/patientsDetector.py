from pymongo import MongoClient

def verify(text, matchers, de_matchers):
	for de_mactcher in de_matchers:
			if de_mactcher in text:
				return False

	for matcher in matchers:
			if matcher in text:
				return True
	return False 




def getPatientsTweets(collection):
	print("Connecting to {}".format(collection.db))
	patients_tweets = []
	matchers = ["I was diagnosed", "I am diagnosed"]
	de_matchers = ["RT @"]

	for tweet in collection.find({"lang": 'en'}):
		text = tweet['text']

		if verify(text, matchers, de_matchers):
			patients_tweets.append(tweet)
			if len(patients_tweets) % 10 == 1:
				print(text)
			


		
	return patients_tweets


def insertTweets(tweets, collectionName):
	collection = MongoClient("localhost", 27017)["idea"][collectionName]
	collection.insert(tweets)
	print("{} tweets inserted".format(len(tweets)))

def writeTweets(tweets, file_name):
	w = open(file_name, 'w')
	for tweet in tweets:
		user_id = tweet['user']['id']
		user_name = tweet['user']['screen_name']
		text = tweet['text']
		w.write("{}\t{}\t{}\n".format(text,user_name,user_id))
	w.close()


def disorderDetect(tweets, matchers):
	postive_tweets = []
	for tweet in tweets:
		text = tweet['text'].lower()
		if verify(text, matchers,[]):
			postive_tweets.append(tweet)
	return postive_tweets




collection = MongoClient('localhost',27017)['idea']['BPD_581_emotion']
#collection = MongoClient('140.114.77.23',27017)['idea']['test']


#patients_tweets = getPatientsTweets(collection)

#insertTweets(patients_tweets, "paitents_tweets")

#matchers = ['bipolar','MDD', 'depressive','bpd','ptsd','sad','depression']
#postive_tweets = disorderDetect(patients_tweets, matchers)