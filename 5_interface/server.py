from flask import Flask, render_template, request, jsonify
import requests
import os
from sklearn.externals import joblib
from idCrawler import getTweets, getUserProfile
from data_transformation import pol_report
from data_transformation import generate_timeline
import json


bipolar_unigrams = set(json.load(open("bipolar_unigrams_3000.json")))

BPD_unigrams = set(json.load(open("BPD_unigrams_3000.json")))

def tweets_2_words_frequency(tweets):
    bipolar_words = {}
    BPD_words = {}
    for tweet in tweets:
        text = tweet["text"].strip().lower().split()
        for word in text:
            if word in bipolar_unigrams:
                bipolar_words[word] = bipolar_words.get(word,0) + 1
            if word in BPD_unigrams:
                BPD_words[word] = BPD_words.get(word,0) + 1

    bipolar_words = sorted([[word,count] for word, count in bipolar_words.items()],key=lambda x: -x[1])
    BPD_words = sorted([[word,count] for word, count in BPD_words.items()],key=lambda x: -x[1])

    return bipolar_words, BPD_words


app = Flask(__name__)


@app.route('/predict_json_by_id')
def getPrediction_json_by_id():
    result = {}
    if request.method == "GET":
        #try:
        user_id = request.args['user_id']
       
        tweets = getTweets(user_id=user_id)
        timeline = generate_timeline(tweets)
        report = pol_report(tweets)
        profile = getUserProfile(user_id=user_id)
        profile["profile_image_url"] = profile["profile_image_url"].replace("normal.", "400x400.")
        #result = {"profile": profile, "report":report}
        bipolar_words, BPD_words = tweets_2_words_frequency(tweets)
        return jsonify(profile=profile, report=report, bipolar_words = bipolar_words, BPD_words = BPD_words, timeline = timeline)
        

# main route for comparing two twitter users

@app.route('/predict_json_by_name')
def getPrediction_json_by_name():
    result = {}
    if request.method == "GET":
        #try:
        screen_name = request.args['screen_name']
        tweets = getTweets(screen_name=screen_name)
        timeline = generate_timeline(tweets)
        report = pol_report(tweets)
        profile = getUserProfile(screen_name=screen_name)
        profile["profile_image_url"] = profile["profile_image_url"].replace("normal.", "400x400.")
        #result = {"profile": profile, "report":report}
        bipolar_words, BPD_words = tweets_2_words_frequency(tweets)
        return jsonify(profile=profile, report=report, bipolar_words = bipolar_words, BPD_words = BPD_words, timeline = timeline)
        
    
@app.route('/predict')
def getPrediction():
   
    if request.method == "GET":
        try:
            screen_name = request.args['screen_name']
            tweets = getTweets(screen_name=screen_name)
            report = pol_report(tweets)
            profile = getUserProfile(screen_name=screen_name)
            profile["profile_image_url"] = profile["profile_image_url"].replace("normal.", "400x400.")      

        except Exception as e:
            report = {"result":str(e)}
            profile = report
    
    return render_template('prediction.html',report=report, profile=profile)


@app.route('/', methods=['GET', 'POST'])
def index():
    errors = []
    results = {}
    if request.method == "GET":
        # get url that the user has entered
        try:
            url = "hahaha" + request.args['url']
            errors.append(url)
           
        except:
            errors.append(
                "Unable to get URL. Please make sure it's valid and try again."
            )
    return render_template('index.html', errors=errors, results=results)


if __name__ == '__main__':
    #app.run(debug=True)

    app.run(debug=True, host= '0.0.0.0',port=1024)
