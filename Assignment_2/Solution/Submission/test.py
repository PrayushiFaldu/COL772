# Imports
import re
import sys
import json
import pickle
import numpy as np
import pandas as pd
from time import time
from nltk.stem.snowball import SnowballStemmer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import CountVectorizer,TfidfTransformer
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report, confusion_matrix

stemmer = SnowballStemmer("english", ignore_stopwords=True)

def normalise_words(sent):
	res = []
	for word in sent.split(" "):
		temp = ""
		for idx,char in enumerate(word):
			if(idx < 2):
				temp += char
			else:
				if(not (char.lower() == word[idx-1].lower() and char.lower() == word[idx-2].lower())):
					temp += char
		res.append(temp)	 
	return " ".join(res)


def replace_puncts(sent):
	sent = re.sub(r"(&quot|&amp|\/|\?|,|\.|\-|_|\!|'|\.|\^|\||;|\*)"," ", sent)
	sent = re.sub("[^a-zA-Z@#]"," ",sent)
	sent = re.sub(r"(\s\s*)"," ",sent).strip()
	return sent


def preprocess_text(text):
	# remove urls
	text = re.sub(r"((www\.[^\s]+)|(https?://[^\s]+))","", text) 
	# remove tags
	text = re.sub(r"@[^\s]+","", text) 
	# normalise words : awwwww -> aww
	text = normalise_words(text) 
	# replace puncts and non alphas
	text = replace_puncts(text) 

	return " ".join([stemmer.stem(i) for i in text.strip().split(" ")])

def get_tf_based_stopwords(model_directory):
	tf_stopwords = set()
	
	with open(f"{model_directory}/stopwords.json","r") as infile:
		tf_stopwords = json.load(infile)
	return tf_stopwords["stop_words"]


if __name__=="__main__":

	model_directory = sys.argv[1]
	input_file_path = sys.argv[2]
	output_file_path = sys.argv[3]

	#testing
	# data = pd.read_csv(f"{model_directory}/test.csv",encoding="ISO-8859–1")
	# data.dropna(inplace=True)
	# print(data.head())

	# read data
	data = pd.DataFrame(open(input_file_path,"r").readlines(), columns=["tweet"])

	# Get processed tweets
	print("-"*100)
	print("Pre-processing the data\n")
	data["processed_tweet"] = data.tweet.apply(lambda x: preprocess_text(x))

	# Generate tf based stop words
	print("-"*100)
	print("Generating stop words\n")
	tf_stopwords_set = set(get_tf_based_stopwords(model_directory))

	# remove stopwords from data
	print("-"*100)
	print("Removing stop words\n")
	test_data = []
	for i in data.processed_tweet:
		s = " ".join([x for x in i.split() if x not in tf_stopwords_set])
		test_data.append(re.sub(r"\s\s*"," ",s))


	# initialise count vectorizer
	print("-"*100)
	print("Loading the Vectorizer\n")
	count_vectorizer = pickle.load(open(f'{model_directory}/vectorizer.pkl', 'rb'))

	print("-"*100)
	print("Loading the classifier\n")
	class_obj = open(f'{model_directory}/classifier.pkl', 'rb')	 
	classifier = pickle.load(class_obj)


	print("-"*100)
	print("Predicting class for test data\n")
	test_pred = classifier.predict(count_vectorizer.transform(test_data))

	with open(output_file_path,"w") as f:
		 for i in range(len(test_pred[:])-1):
			 f.write(str(test_pred[i])+"\n")
		 f.write(str(test_pred[i]))
	f.close()

	accuracy = accuracy_score(test_pred, data.label)
	conmat = np.array(confusion_matrix(test_pred, data.label, labels=[0,4]))
	confusion = pd.DataFrame(conmat, index=['negative', 'positive'],
						 columns=['predicted_negative','predicted_positive'])
	print("accuracy score: {0:.2f}%".format(accuracy*100))
	print("-"*80)
	print("Confusion Matrix\n")
	print(confusion)
	print("-"*80)
	print("Classification Report\n")
	print(classification_report(test_pred, data.label, target_names=['negative','positive']))
