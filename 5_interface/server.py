from flask import Flask, render_template, request, jsonify
import requests
import os
from sklearn.externals import joblib
from idCrawler import getTweets, getUserProfile
from data_transformation import pol_report

app = Flask(__name__)




@app.route('/predict')
def getPrediction():
   
    if request.method == "GET":
        try:
            screen_name = request.args['screen_name']
            tweets = getTweets(screen_name=screen_name)
            report = pol_report(tweets)
            profile = getUserProfile(screen_name=screen_name)
            
            

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
    app.run(debug=True)