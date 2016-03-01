import json

file_path = "Dictionaries/LIWC2007_English080730.dic"
categories_output_path = "categories.json"
words_output_path = "words.json"
f = open(file_path, 'r')
categories = {}
words = {}

percent_flags = 0
for line in f:
	if line == "%\n":
		percent_flags += 1
		
		if percent_flags == 2:
			break
		continue
	print(line.strip().split())	
	index, category = line.strip().split()
	categories[index] = category

for line in f:
	segments = line.strip().split()
	print(segments)
	word = segments[0]

	words[word] = segments[1:]

w = open(categories_output_path, "w")
json.dump(categories, w)
w.close()



w = open(words_output_path, "w")
json.dump(words, w)
w.close()
