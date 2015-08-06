from pymongo import MongoClient
from idCrawler import *
from twython import TwythonRateLimitError

def verify(text, matchers, de_matchers):
	for de_mactcher in de_matchers:
			if de_mactcher in text:
				return False

	for matcher in matchers:
			if matcher in text:
				return True
	return False 


def insertTweets(tweets, collectionName):
	collection = MongoClient("localhost", 27017)["idea"][collectionName]
	collection.insert(tweets)
	print("{} tweets inserted".format(len(tweets)))

groups = ['Sectioned_','AmandaGreenUK','bondobbs','OfficialBPDChat','HealingFromBPD', 'bpdguy','bpdsurvive','JurmaineHealth','BPD_BC','SympoPsychiatry','hope4healing','borderlinepd101']
bipolar_groups = ['BipolarDisorder', 'BipolarRecovery', 'BipolarUK', 'PsychCentral', 'DBSAlliance', 'NLOBipolar', 'BipolarUs','Skytherapist', 'chatobstewart', 'natasha_tracy', 'erin_michalak', 'CREST_BD', 'namiohio', 'ResearchAtCRI','Bipolar_Blogs',' _BipolarManiac', 'YoungMindsUK']
print("Followers collections")
followers = []
for screen_name in bipolar_groups:
	followers += getFollowers(screen_name)
followers = list(set(followers))

print("Followers profiles collections")
user_profiles = []
lost_ids = []
for i, user_id in enumerate(followers[len(user_profiles):]):
	user_profile = getUserProfile(user_id)
	if user_profile != []:
		user_profiles.append(user_profile)


print("Collection finsihed")


matchers = ['borderline','bpd','disorder','ptsd','depression','mdd','depressive']
positive_users = []		
for user_profile in user_profiles:
	description = user_profile['description'].lower()
	if verify(description, matchers, []):
		positive_users.append(user_profile)

print("Positive users: {}".format(len(positive_users)))
