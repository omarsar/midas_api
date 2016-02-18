import numpy as np
import pandas as pd
from pymongo import MongoClient
from bokeh.plotting import figure, output_file, show, VBox
import datetime



def dateCount(collection="regularUser_en_fixed", tweets = None):
    dateCount ={}

    if tweets is None:

        client = MongoClient('localhost', 27017)
        collection = client['idea'][collection]
     
        for tweet in collection.find():
            date =  np.datetime64(tweet["created_at"].date().strftime("%Y-%m-%d"))
            dateCount[date] = dateCount.get(date,0) + 1
        return pd.DataFrame(list(dateCount.items())).sort([0])

    else:
        for tweet in tweets:
            date =  np.datetime64(tweet["created_at"].date().strftime("%Y-%m-%d"))
            dateCount[date] = dateCount.get(date,0) + 1
        return pd.DataFrame(list(dateCount.items())).sort([0])
        


def getUserTweets(collectionName):
    client = MongoClient('localhost', 27017)
    collection = client['idea'][collectionName]
    userTweets = {}
    for tweet in collection.find():
        dataPoint = {"created_at": tweet["created_at"]}
        userID = tweet["user"]["id"]
        if  userID in userTweets:
            userTweets[userID].append(dataPoint)
        else:
            userTweets[userID] = [dataPoint]
    return userTweets

userTweets = getUserTweets("regularUser_en_fixed")
users = list(userTweets.keys())


user_1_tweets = userTweets[users[0]] 
user_2_tweets = userTweets[users[1]]

user_1_data = dateCount(tweets=user_1_tweets)
user_2_data = dateCount(tweets=user_2_tweets)

# Here is some code to read in some stock data from the Yahoo Finance API

BPD_tweets = dateCount('BDP_tweets')


regular_tweets = dateCount('regularUser_en_fixed')

output_file("tweets_distribution_fixed.html", title="Tweets Distribution")

# create a figure
p1 = figure(title="Tweets",
            x_axis_label="Date",
            y_axis_label="Post Count",
            x_axis_type="datetime")

p2 = figure(title="Tweets",
            x_axis_label="Date",
            y_axis_label="Post Count",
            x_axis_type="datetime")

p1.below[0].formatter.formats = dict(years=['%Y'],
                                     months=['%b %Y'],
                                     days=['%d %b %Y'])


p2.below[0].formatter.formats = dict(years=['%Y'],
                         months=['%b %Y'],
                         days=['%d %b %Y'])

# EXERCISE: finish this line plot, and add more for the other stocks. Each one should
# have a legend, and its own color.
p1.line(
    BPD_tweets[0],                                       # x coordinates
    BPD_tweets[1],                                  # y coordinates
    color='#A6CEE3',                                    # set a color for the line
    legend='BPD People',                                      # attach a legend label
)

p2.line(
    regular_tweets[0],                                       # x coordinates
    regular_tweets[1],                                  # y coordinates
    color='#E09926',                                    # set a color for the line
    legend='Regular People',                                      # attach a legend label
)




# EXERCISE: style the plot, set a title, lighten the gridlines, etc.
p1.title = "BDP Tweets along with Time"
p1.grid.grid_line_alpha=0.3

p2.title = "Regular Tweets along with Time"
p2.grid.grid_line_alpha=0.3

# EXERCISE: start a new figure

# Here is some code to compute the 30-day moving average for AAPL


window_size = 30
window = np.ones(window_size)/float(window_size)

# EXERCISE: plot a scatter of circles for the individual AAPL prices with legend


show(VBox(p1,p2))  # open a browser
