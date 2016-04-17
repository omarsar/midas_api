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

getDict =  lambda timeSeries, i: json.loads(timeSeries.iloc[i].to_json())





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


def comboTracker(timeSeries, attribute= "polarity", time_threshold = 120):
    array = timeSeries[attribute]
    starter = array[0]
    combo = 1
    result = []
    index = 0
    for cursor in array[1:]:
        index += 1
        if starter == cursor and timeSeries["dt"][index-1] < time_threshold:
            combo += 1
        else:
            if combo > 1:
                result.append((starter, combo, index-combo))
            starter = cursor
            combo = 1
    if combo > 1:
         result.append((starter, combo, index-combo))
    return result




def getCombosCount(timeSeries, matcher = -1, lowerbound = 2):
    combos = comboTracker(timeSeries)
    combos_count = sum([hit for element, hit, index in combos if element == matcher and hit > lowerbound])
    return combos_count
    




def getFlipsCount(timeSeries, upperbound=60, lowerbound = 0):
    flips = getFlips(timeSeries)
    durations = getFlipsDuration(timeSeries, flips)
    return np.sum((durations > lowerbound) & (durations < upperbound) )



            
      


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
        





def getCombosTweets(timeSeries,lowerbound=2):
    combo_tweets = {"neg_tweets":[], "pos_tweets": []}
    combo_result = comboTracker(timeSeries)
    for polarity, hits, index in combo_result:
        if polarity == -1 and hits > lowerbound:
            combo_tweet = []
            for i in range(index, index+hits):
                combo_tweet.append(getDict(timeSeries, i))
            combo_tweets["neg_tweets"].append(combo_tweet)
        if polarity == 1 and hits > lowerbound:
            combo_tweet = []
            for i in range(index, index+hits):
                combo_tweet.append(getDict(timeSeries,i))
            combo_tweets["pos_tweets"].append(combo_tweet)
    return combo_tweets

def getFlipsTweets(timeSeries, upperbound=60):
    flips = getFlips(timeSeries)
    show_index = np.zeros(timeSeries.shape[0],dtype=bool)
    flip_tweets = []
    for i, value in enumerate(flips):
        if value and timeSeries["dt"][i] < upperbound:

            tweet_a = getDict(timeSeries, i)
            tweet_b = getDict(timeSeries, i+1)
            flip_tweets.append([tweet_a,tweet_b])



    return flip_tweets
        





def getPOLFeature(groups):
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
            negative_combos = getCombosCount(timeSeries) / tweets_length
            positive_combos = getCombosCount(timeSeries,matcher=1) / tweets_length

    
            age = getAge(timeSeries)
            gender = getGender(timeSeries)
            
            feature[i][0] = tweets_rate 
            feature[i][1] = mentio_rate
            feature[i][2] = unique_mentions
            feature[i][3] = frequent_mentions 
            feature[i][4] = positive_ratio
            feature[i][5] = negative_ratio
            feature[i][6] = flips_ratio
            feature[i][7] = negative_combos
            feature[i][8] = positive_combos
            feature[i][9] = age
            feature[i][10] = gender
            
        features.append(feature)
    return features[0]


    






def getTimeSeries(tweets):
	polared_tweets = sentiment_analyize(tweets)
	processed_tweets = getUsersPolarities(polared_tweets)
	timeSeries = timeSeriesTransform(processed_tweets)
	
	return timeSeries

	
def tweets_transform_tfidf(tweets):
	text = ""
	for tweet in tweets:
		text += tweet["text"]
	return tfidf_vectorizor.transform(text)

def tfidf_classify(tweets):
	x = tweets_transform_tfidf(tweets)
	result = tfidf_model.predict_proba([x])
	return result[0]


def getLabeledTweets(timeSeries,label, k =5):
    tweets = []
    for i in range(timeSeries.shape[0]):
        if timeSeries["polarity"][i] == label:
            tweets.append(getDict(timeSeries, i))
            if len(tweets) >= k:
                return tweets
    return tweets



def pol_report(tweets):

    timeSeries_list = getTimeSeries(tweets)
    features = getPOLFeature([timeSeries_list])
    feature = features[0]
    timeSeries = timeSeries_list[0]
    bipolar_proba = bipolar_model.predict_proba(features)[0][1]
    BPD_proba = BPD_model.predict_proba(features)[0][1]
    
    report = {}
    report["tweets_length"] = len(tweets)
    report["tweeting_frequency"] = feature[0]
    report["mentioning_frequency"] = feature[1]
    report["unique_mentioning"] = feature[2]
    report["frequent_mentioning"] = feature[3]
    report["positive_ratio"] = feature[4]
    report["negative_ratio"] = feature[5]
    report["flips_ratio"] = feature[6]
    report["negative_combos"] = feature[7]
    report["positive_combos"] = feature[8]
    report["age"] = features[0][9]
    report["gender"] = "Male" if features[0][10] < 0 else "Female"
    report["bipolar_probability"] = bipolar_proba
    report["BPD_probability"] = BPD_proba
    report["flip_tweets"] = getFlipsTweets(timeSeries)
    report["combo_tweets"] = getCombosTweets(timeSeries)
    report["negative_tweets"] = getLabeledTweets(timeSeries, label=-1)
    report["positive_tweets"] = getLabeledTweets(timeSeries, label = 1)

    return report



def load_model(file_location):
    model = joblib.load(file_location)
    return model 




print("Start loding scikit-lear models:")

print("Loding Bipolar Random Forest")
bipolar_model = load_model("models/bipolar_forest/bipolar_forest")
print("Loding BPD Random Forest")
BPD_model = load_model("models/BPD_forest/BPD_forest")
print("Loading Max Min Scaler")
scaler = load_model("models/scaler/scaler")

print("All models loaded")


if __name__ ==  '__main__':
    print("hi")
