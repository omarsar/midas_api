import csv


age_intercept = 23.2188604687
gender_intercept = -0.06724152


def load_age_lexica(file_name = "emnlp14age.csv"):
	age_lexica = {}
	with open(file_name, mode='r') as infile:
	    reader = csv.DictReader(infile)
	    for data in reader:
	    	weight = float(data['weight'])
	    	term = data['term']
	    	age_lexica[term] = weight

	del age_lexica['_intercept']
	return age_lexica


def load_gender_lexica(file_name = "emnlp14gender.csv"):
	gender_lexica = {}
	with open(file_name, mode='r') as infile:
	    reader = csv.DictReader(infile)
	    for data in reader:
	    	weight =  float(data['weight'])
	    	term = data['term']
	    	gender_lexica[term] = weight

	del gender_lexica['_intercept']
	return gender_lexica

age_lexica = load_age_lexica()
gender_lexica = load_gender_lexica()



# This function returns a float. Positive valuse represents female and vice versa.
def get_gender(text):
	words = text.split()

	text_scores = {}
	for word in words:
		text_scores[word] = text_scores.get(word, 0) + 1

	gender = 0
	words_count = 0
	for word, count in text_scores.items():
		if word in gender_lexica:
			words_count += count
			gender += count * gender_lexica[word]
            
		if words_count <= 0:
			return 0
		else:

			gender = gender / words_count + gender_intercept

			return gender
	
# This function returns a float, representing the age. 

def get_age(text):
	words = text.split()

	text_scores = {}
	for word in words:
		text_scores[word] = text_scores.get(word, 0) + 1

	age = 0
	words_count = 0
	for word, count in text_scores.items():
		if word in age_lexica:
			words_count +=count
			age += count * age_lexica[word]
	if words_count <= 0:
		return -1
	else:
		age = age / words_count + age_intercept

		return age

