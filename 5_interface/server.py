from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)


@app.route('/json')
def getJSON():
    result = {"yes":"baby"}
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