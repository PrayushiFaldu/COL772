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


def compute_tf_matrix(processed_tweets, labels):
	tf_dict = {}
	class_map = {"0":"neg","4":"pos"}
	for sent,label in zip(processed_tweets, labels):
		for word in sent.lower().split(" "):
			if(not word in tf_dict):
				tf_dict.update({word:{"neg":0,"pos":0}})
			tf_dict[word][class_map[str(label)]] += 1

	tf_df = pd.DataFrame.from_dict(tf_dict,orient='index')
	
	tf_df["diff"] = tf_df.apply(lambda x : abs(x["neg"]-x["pos"]), axis=1)
	tf_df["count"] = tf_df.apply(lambda x : abs(x["neg"]+x["pos"]), axis=1)
	
	num_chars = []
	for word in tf_df.index.values.tolist():
		num_chars.append(len(set(word)))
	
	tf_df["num_chars"] = num_chars
	return tf_df

def get_tf_based_stopwords(processed_tweets, labels):
	tf_stopwords = []
	tf_thres = 50
	# normalised_diff_thres = 0.3

	tf_df = compute_tf_matrix(processed_tweets, labels)

	# tf_stopwords.extend(tf_df.sort_values(["count"], ascending=False).head(tf_thres).index.tolist())
	# tf_stopwords.extend(tf_df[tf_df["normalised_diff"] <= 0.30].sort_values("normalised_diff", ascending=False).index.tolist())

	tf_stopwords.extend(tf_df[(tf_df["neg"]==0) & (tf_df["pos"]<=25)].index.tolist())
	tf_stopwords.extend(tf_df[(tf_df["neg"]<=25) & (tf_df["pos"]==0)].index.tolist())
	tf_stopwords.extend(tf_df[(tf_df["num_chars"]==1)].index.tolist())

	return tf_stopwords


if __name__=="__main__":

	start_time = time()

	data_directory = sys.argv[1]
	model_directory = sys.argv[2]

	print(data_directory)
	print(model_directory)

	# read data
	input_data_read_path = f"{data_directory}/training.csv"
	data = pd.read_csv(input_data_read_path, encoding="ISO-8859–1", header=None, names=["label","tweet"])

	# Get processed tweets
	print("-"*100)
	print("Pre-processing the data\n")
	data["processed_tweet"] = data.tweet.apply(lambda x: preprocess_text(x))

	# Generate tf based stop words
	print("-"*100)
	print("Generating stop words\n")
	tf_stopwords = get_tf_based_stopwords(data.processed_tweet.values.tolist(), data.label.values.tolist())

	# remove stopwords from data
	print("-"*100)
	print("Removing stop words\n")
	x = []
	y = []
	tf_stopwords_set = set(tf_stopwords)
	for i,l in zip(data.processed_tweet, data.label):
		s = " ".join([x for x in i.split() if x not in tf_stopwords_set])
		x.append(re.sub(r"\s\s*"," ",s))
		y.append(l)

	stopwords_dict = {"stop_words" : list(tf_stopwords_set)}
	out_file = open(f"{model_directory}/stopwords.json", "w")
	json.dump(stopwords_dict, out_file, indent = 4)


	X = pd.DataFrame(x, columns=["tweet"])
	Y = pd.DataFrame(y, columns=["label"])

	x_train = X.tweet
	y_train = Y.label
	
	# split test train data
	# SEED= 2000
	# x_train, x_test, y_train, y_test = train_test_split(X.tweet, Y.label, test_size=0.01, random_state=SEED)

	# print(f"Train set size: {len(x_train)}, +ve set size: {len(x_train[y_train == 4])}, -ve set size: {len(x_train[y_train == 0])}")
	# print(f"Test set size: {len(x_test)}, +ve set size: {len(x_test[y_test == 4])}, -ve set size: {len(x_test[y_test == 0])}")


	# test_df = pd.DataFrame(columns=["tweet","label"])
	# test_df["tweet"] = x_test
	# test_df["label"] = y_test
	# test_df.to_csv(f"{model_directory}/test.csv")

	# initialise countvectorizer
	print("-"*100)
	print("Fitting the Vectorizer")
	corpus = x_train.values.tolist()
	count_vectorizer = CountVectorizer(analyzer='word', ngram_range=(1, 3))
	cvec = count_vectorizer.fit_transform(corpus)

	pickle.dump(count_vectorizer,open(f"{model_directory}/vectorizer.pkl","wb"))

	# Fit the classifier
	print("-"*100)
	print("Fitting the classifier")
	lr = LogisticRegression(penalty='l1', solver='liblinear')
	lr_fit = lr.fit(cvec, y_train)

	pickle.dump(lr_fit, open(f"{model_directory}/classifier.pkl","wb"))

	print(f"Total execution time : {round((time()-start_time)/60,3)}")