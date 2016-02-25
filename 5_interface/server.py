from flask import Flask, render_template, request, jsonify
import requests
import os
from sklearn.externals import joblib
from idCrawler import getTweets
from data_transformation import tfidf_classify, pol_classify

app = Flask(__name__)




@app.route('/predict')
def getJSON():
   
    if request.method == "GET":
        try:
            screen_name = request.args['screen_name']
            tweets = getTweets(screen_name=screen_name)
            proba = pol_classify(tweets)
            result = {"Probability of having BPD": proba[1]}

        except Exception as e:
            result = {"result":str(e)}
    
    return jsonify(result)


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