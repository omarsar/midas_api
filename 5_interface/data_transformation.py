from datetime import datetime
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk import PorterStemmer
import re
from scipy.sparse import hstack
from scipy.sparse import vstack
import age_gender_predictor
from copy import copy
import pandas as pd
from Levenshtein import *
from sklearn.externals import joblib
from urllib.request import urlopen
from idCrawler import getTweets
import json

def thirdPronuonDetect(words, matcher=re.compile("@[a-z]+")):
    for word in words:
        if word == "@":
            continue
        elif matcher.search(word):
            return True
    return False

def tweetRate(timeSeries):
    total_tweets = timeSeries.shape[0]
    delta_time = np.max(timeSeries.index.values) - np.min(timeSeries.index.values)
    totla_duration = (delta_time).astype('timedelta64[h]') / np.timedelta64(24, 'h')
    return total_tweets / totla_duration
def mentioRate(timeSeries):
    total_tweets = timeSeries.shape[0]
    total_mentions = np.sum(seriesContains(timeSeries, method="third"))
    return total_mentions / total_tweets

def uniqueMentions(timeSeries):
    total_tweets = timeSeries.shape[0]
    friends_set = set()
    texts = timeSeries["text"].values
    for text in texts:
        terms = text.strip().split()
        for word in terms:
            if word[0] == '@' and len(word) > 1:
                friends_set.add(word)
    return len(friends_set)

def frequentMentions(timeSeries, lowerbound = 3):
    total_tweets = timeSeries.shape[0]
    friends_mentions = {}
    texts = timeSeries["text"].values
    for text in texts:
        terms = text.strip().split()
        for word in terms:
            if word[0] == '@' and len(word) > 1:
                friends_mentions[word] = friends_mentions.get(word, 0) +1
    frequent_frients = [screen_name for screen_name, mentions in friends_mentions.items() if mentions >= lowerbound]
    return len(frequent_frients)

def getNegativeRatio(timeSeries):
    total_tweets = timeSeries.shape[0]
    return np.sum(timeSeries["polarity"].values == -1) / total_tweets


def getPositiveRatio(timeSeries):
    total_tweets = timeSeries.shape[0]
    return np.sum(timeSeries["polarity"].values == 1) / total_tweets


def sentiment_analyize(tweets):
    payload = {"data": [],"language": "en"}
    
    for tweet in tweets:
        payload["data"].append({"text": tweet["text"],"id": tweet["id"]})
    
    payload = json.dumps(payload).encode('utf-8')
    response = urlopen('http://www.sentiment140.com/api/bulkClassifyJson?appid=ccha97u@gmail.com', payload) # request to server
    results = response.read().decode('"ISO-8859-1"') # get the response
    results = json.loads(results)['data']
    for i,result in enumerate(results):
       
        if result['polarity'] == 0:
            tweets[i]["polarity"] = "negative"
        elif result['polarity'] == 2:
            tweets[i]["polarity"] = "neutral"
        elif result['polarity'] == 4:
            tweets[i]["polarity"] = "positive"
        else:
             tweets[i]["polarity"] = "unknown"
    return tweets


# new functions

def getAge(timeSeries):
    texts = ""
    for text in timeSeries["text"].values:
        texts += text + "\n"
    return age_gender_predictor.get_age(texts)

def getGender(timeSeries):
    texts = ""
    for text in timeSeries["text"].values:
        texts += text + "\n"
    return age_gender_predictor.get_gender(texts)
        



def getNegativeCount(timeSeries):
    return np.sum(timeSeries["polarity"].values == -1)


def getUsersPolarities(tweets):
	usersPolarties = {}

	for tweet in tweets:
	    userID = tweet["user"]["id"]
	   
	   
	   

	    if tweet["polarity"] == "positive":
	        polarity = 1
	    elif tweet["polarity"] == "negative":
	        polarity = -1
	    else:
	        polarity = 0

	        
	    date = tweet["created_at"]
	    text = tweet['text']

	    if userID not in usersPolarties:
	        usersPolarties[userID] = {}
	    if date not in usersPolarties[userID]:
	        usersPolarties[userID][date] = {}
	    usersPolarties[userID][date]['text'] = text
	    usersPolarties[userID][date]['polarity'] =  polarity
	   
	return usersPolarties


def timeSeriesTransform(usersEmotions):
    for userID in usersEmotions:
        usersEmotions[userID] = pd.DataFrame.from_dict(usersEmotions[userID], orient='index').fillna(0)
        usersEmotions[userID]['dt'] = np.zeros(usersEmotions[userID].shape[0],dtype=float)
        usersEmotions[userID].loc[:-1,'dt'] = (usersEmotions[userID].index[1:].values - usersEmotions[userID].index[:-1].values).astype('timedelta64[s]') / np.timedelta64(60, 's')
    return list(usersEmotions.values())



def userVerify(timeSeries, threshold = 0.5, lowerbound = 50):
    http_rows = getHTTPRows(timeSeries)
    average_http_count = np.sum(http_rows) / timeSeries.shape[0]
    duration = np.max(timeSeries.index.values) -  np.min(timeSeries.index.values)
    duration = duration.astype('timedelta64[s]') / np.timedelta64(604800, 's')
    return (average_http_count < threshold) and (timeSeries.shape[0] > lowerbound) and duration > 1


def groupFilter(group):
    new_group = []
    for timeSeries in group:
        if userVerify(timeSeries):
            new_group.append(cleanPost(timeSeries))
    return new_group




def comboTracker(timeSeries, attribute= "polarity"):
    array = timeSeries[attribute]
    starter = array[0]
    combo = 1
    result = []
    for cursor in array[1:]:
        if starter == cursor:
            combo += 1
        else:
            if combo > 1:
                result.append((starter, combo))
            starter = cursor
            combo = 1
    if combo > 1:
         result.append((starter, combo))
    return result

def getHTTPRows(timeSeries):
    count = 0
    patterns = ['http://','https://']
    conditions = timeSeries['text'].str.contains(patterns[0])
    for pattern in patterns[1:]:
        conditions = conditions | timeSeries['text'].str.contains(pattern)

    return conditions.values


def cleanPost(timeSeries):
    left_text = timeSeries['text'].values[:-1]
    right_text = timeSeries['text'].values[1:]
    conditions = np.ones(timeSeries.shape[0],dtype=bool)
    edit_distance = np.vectorize(distance)
    conditions[:-1] =  conditions[:-1] & (edit_distance(left_text, right_text) > 5)
    patterns = ['http://','https://']
    
    for pattern in patterns:
        conditions = conditions & np.logical_not(timeSeries['text'].str.contains(pattern).values)
    timeSeries = timeSeries[conditions]
    timeSeries.loc[:,'dt'] = np.zeros(timeSeries.shape[0],dtype=float)
    timeSeries.loc[:-1,'dt'] = (timeSeries.index[1:].values - timeSeries.index[:-1].values).astype('timedelta64[s]') / np.timedelta64(60, 's')

    return timeSeries


def getFlipsDuration(timeSeries, flips):
    timeSeries = timeSeries[flips]
    timeSeries.loc[:,'dt'] = np.zeros(timeSeries.shape[0],dtype=float)
    timeSeries.loc[:-1,'dt'] = (timeSeries.index[1:].values - timeSeries.index[:-1].values).astype('timedelta64[s]') / np.timedelta64(60, 's')
    return timeSeries['dt'][:-1].values



def getFlips(timeSeries, attribute= 'polarity'):
    flips = np.zeros(timeSeries.shape[0],dtype=bool)
    polarity = timeSeries[attribute].values[:-1]
    right_elements = timeSeries[attribute].values[1:]
    flips[:-1] = (polarity * right_elements) < 0
    return flips

def seriesContains(timeSeries,method ="first"):
    if method == "first":
        match_function = np.vectorize(firstPronuonDetect)
    elif method == "second":
        match_function = np.vectorize(secondPronuonDetect)
    elif method == "third":
            match_function = np.vectorize(thirdPronuonDetect)


    return match_function(timeSeries["text"].str.lower().str.split().values)
    

def firstPronuonDetect(words, matchers=["i","we","i'd","i'm"]):
    for matcher in matchers:
        if matcher in words:
            return True
    return False


def getFirstPronounCount(timeSeries):
    return np.sum(seriesContains(timeSeries))

def comboTracker(timeSeries, attribute= "polarity"):
    array = timeSeries[attribute]
    starter = array[0]
    combo = 1
    result = []
    for cursor in array[1:]:
        if starter == cursor:
            combo += 1
        else:
            if combo > 1:
                result.append((starter, combo))
            starter = cursor
            combo = 1
    if combo > 1:
         result.append((starter, combo))
    return result




def getCombosCount(timeSeries, matcher = -1, lowerbound = 2):
    combos = comboTracker(timeSeries)
    combos_count = sum([hit for element, hit in combos if element == matcher and hit > lowerbound])
    return combos_count
    


def getFlips(timeSeries, attribute= 'polarity'):
    flips = np.zeros(timeSeries.shape[0],dtype=bool)
    polarity = timeSeries[attribute].values[:-1]
    right_elements = timeSeries[attribute].values[1:]
    flips[:-1] = (polarity * right_elements) < 0
    return flips

def getFlipsCount(timeSeries, upperbound=30, lowerbound = 0):
    flips = getFlips(timeSeries)
    durations = getFlipsDuration(timeSeries, flips)
    return np.sum((durations > lowerbound) & (durations < upperbound) )



def getFlipsDuration(timeSeries, flips):
    timeSeries = timeSeries[flips]
    timeSeries.loc[:,'dt'] = np.zeros(timeSeries.shape[0],dtype=float)
    timeSeries.loc[:-1,'dt'] = (timeSeries.index[1:].values - timeSeries.index[:-1].values).astype('timedelta64[s]') / np.timedelta64(60, 's')
    return timeSeries['dt'][:-1].values




            
            
            
      


def getEmotionRatio(timeSeries):
    emotions = ['surprise', 'fear', 'sadness', 'disgust', 'trust', 'anticipation', 'anger','joy']
    emotion_ratios = []
    conditions = np.logical_not(timeSeries["ambiguous"].values)
    timeSeries = timeSeries[conditions]

    for emotion in emotions:
        total = np.sum((timeSeries["emotion"].values == emotion))
        emotion_ratio = total / timeSeries.shape[0]
        emotion_ratios.append(emotion_ratio)
        
    return emotion_ratios
        





def getPolFeature(groups):
    features = []
    for group in groups:
        feature = np.zeros((len(group),11),dtype=float)
        for i, timeSeries in enumerate(group):
            tweets_length = timeSeries.shape[0]
            tweets_rate = tweetRate(timeSeries)
            mentio_rate = mentioRate(timeSeries)
            unique_mentions = uniqueMentions(timeSeries)
            frequent_mentions = frequentMentions(timeSeries)
            negative_ratio = getNegativeRatio(timeSeries)
            positive_ratio = getPositiveRatio(timeSeries)
            flips_ratio = getFlipsCount(timeSeries) / tweets_length
            combos_ratio = getCombosCount(timeSeries) / tweets_length
            first_pronoun_ratio = getFirstPronounCount(timeSeries) / tweets_length
            age = getAge(timeSeries)
            gender = getGender(timeSeries)
            
            feature[i][0] = tweets_rate 
            feature[i][1] = mentio_rate
            feature[i][2] = unique_mentions
            feature[i][3] = frequent_mentions 
            feature[i][4] = positive_ratio
            feature[i][5] = negative_ratio
            feature[i][6] = flips_ratio
            feature[i][7] = combos_ratio
            feature[i][8] = first_pronoun_ratio
            feature[i][9] = age
            feature[i][10] = gender
            #feature[i][11:] = getEmotionRatio(timeSeries)
        features.append(feature)
    return features[0]

    
    






def tweets_transform_pol(tweets):
	polared_tweets = sentiment_analyize(tweets)
	processed_tweets = getUsersPolarities(polared_tweets)
	timeSeries = timeSeriesTransform(processed_tweets)
	feature = getPolFeature([timeSeries])
	return feature

	
def tweets_transform_tfidf(tweets):
	text = ""
	for tweet in tweets:
		text += tweet["text"]
	return tfidf_vectorizor.transform(text)

def tfidf_classify(tweets):
	x = tweets_transform_tfidf(tweets)
	result = tfidf_model.predict_proba([x])
	return result[0]

def pol_classify(tweets):
	timeSeries = tweets_transform_pol(tweets)
	result = pol_model.predict_proba(timeSeries)
	return result[0]



def load_model(file_location):
    model = joblib.load(file_location)
    return model 



tfidf_model = load_model("models/tfidf_forest/tfidf_forest")
pol_model = load_model("models/pol_forest/pol_forest")
tfidf_vectorizor = load_model("models/tfidf_vectorizor/tfidf_vectorizor")

