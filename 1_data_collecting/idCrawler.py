# A python module written by GB to donwload user profiles and user tweets



from twython import Twython
from  twython import TwythonRateLimitError
from langdetect import detect
from langdetect.detector import LangDetectException
from time import sleep
from twython import Twython
from twython import TwythonAuthError
from twython import TwythonRateLimitError
from twython import TwythonError
from warnings import warn
from datetime import datetime

def getTweets(screen_name=None, user_id=None, num = 0, include_rts = False):
	consumer_key = "MLGdNZCfmzGthHTAyJU4KFvbU"
	consumer_secret ="Tfp7DIZcJLbnS8BR5CWQmZklrhsbtc3fMfssKPT4SZoYsPiQKw"
	access_token ="2383540880-s2C8xPgA4ITF7QnLRFnHK1es2UEbmW8qHQ87sX5"
	access_token_secret ="kLYgBTPeslLgaFugCx0PoiBpPIKnyCBEVfqqJCkjsSKpP"
	twitter = Twython(consumer_key, consumer_secret,access_token,access_token_secret )

	tweets = None
	while(tweets == None):
		try:
			if screen_name == None:
				tweets = twitter.get_user_timeline(user_id = user_id, count = 200, trim_user = False, include_rts = include_rts  )
			else:
				tweets = twitter.get_user_timeline(screen_name = screen_name, count = 200, trim_user = False, include_rts = include_rts  )
		except TwythonRateLimitError:
			warn("Fall asleep")
			sleep(300)
			pass
		except  TwythonAuthError:
			warn("Bad Authentication")
			return []
		except TwythonError:
			warn("404 not found")
			return []



	totalTweets = tweets
	while len(tweets) >= 2:
		max_id = tweets[-1]["id"]
		try:
			if screen_name == None:
				tweets = twitter.get_user_timeline(user_id = user_id, max_id = max_id, count = 200, trim_user = False, include_rts = include_rts )
			else:
				tweets = twitter.get_user_timeline(screen_name = screen_name, max_id = max_id, count = 200, trim_user = False, include_rts = include_rts )

		except TwythonRateLimitError:
			print("Fall asleep")
			sleep(300)
			continue

		if len(tweets) > 1:
			totalTweets += tweets[1:]
		elif num > 0 and len(tweets) >= num :
			break
		

	for i in range(len(totalTweets)):
		date = totalTweets[i]["created_at"]
		totalTweets[i]["created_at"] = datetime.strptime(date, '%a %b %d %H:%M:%S +0000 %Y')
	
	if num == 0:
		return totalTweets
	else:
		return totalTweets[:num]

	
	

def langDetect(tweets ,lang, threshold, method = "simple"):
	if len(tweets) == 0:
		return False
	langCount = 0
	if method == "simple":
		for tweet in tweets:
			try:
				if lang == tweet["lang"]:
					langCount += 1
			except LangDetectException:
				pass
	else:
		for tweet in tweets:
			try:
				if lang == detect(tweet["text"]):
					langCount += 1
			except LangDetectException:
				pass
	langRatio = langCount / len(tweets)
	print(langRatio)


	return langRatio > threshold



def userLangDetect(screen_name=None, user_id=None, lang="en", threshold=0.9, num = 200):
	if screen_name == None:
		tweets = getTweets(screen_name=None,user_id=user_id)
	else:
		tweets = getTweets(screen_name)
	return langDetect(tweets,lang,threshold)


def getFollowers(screen_name):
	consumer_key = "MLGdNZCfmzGthHTAyJU4KFvbU"
	consumer_secret ="Tfp7DIZcJLbnS8BR5CWQmZklrhsbtc3fMfssKPT4SZoYsPiQKw"
	access_token ="2383540880-s2C8xPgA4ITF7QnLRFnHK1es2UEbmW8qHQ87sX5"
	access_token_secret ="kLYgBTPeslLgaFugCx0PoiBpPIKnyCBEVfqqJCkjsSKpP"
	twitter = Twython(consumer_key, consumer_secret,access_token,access_token_secret )


	while(True):
		try:
			followers = twitter.get_followers_ids(screen_name = screen_name)	
			followers_id = followers['ids']
			return followers_id		
		except TwythonRateLimitError:
			print("Fall asleep")
			sleep(300)
			pass
		except wythonError:
			print("404 not found")
			return []
		except TwythonAuthError:
			print("Bad Authentication")
			return []







def getUserProfile(user_id):
	consumer_key = "MLGdNZCfmzGthHTAyJU4KFvbU"
	consumer_secret ="Tfp7DIZcJLbnS8BR5CWQmZklrhsbtc3fMfssKPT4SZoYsPiQKw"
	access_token ="2383540880-s2C8xPgA4ITF7QnLRFnHK1es2UEbmW8qHQ87sX5"
	access_token_secret ="kLYgBTPeslLgaFugCx0PoiBpPIKnyCBEVfqqJCkjsSKpP"
	twitter = Twython(consumer_key, consumer_secret,access_token,access_token_secret )
	while(True):
		try:
			user_profile = twitter.show_user(id = user_id)
			return user_profile
		except TwythonRateLimitError:
			print("Fall asleep")
			sleep(300)
			pass
		except  TwythonAuthError:
			print("Bad Authentication")
			return []
		except TwythonError:
			print("404 not found")
			return []

	
	







if __name__ == '__main__':
	print(getTweets(screen_name="BigDataBlogs", num =10))
	
