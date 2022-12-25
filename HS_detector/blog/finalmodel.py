import nltk
import string
import pandas as pd
import numpy as np
import re
import string
from matplotlib import pyplot as plt
from nltk.stem.porter import *
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
#from textstat.textstat import *
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer as VS
nltk.download('vader_lexicon')
from textstat.textstat import textstat
from wordcloud import WordCloud
#%matplotlib inline
from matplotlib import pyplot as plt
from PIL import Image
from gensim.test.utils import common_texts
import seaborn
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn import svm
from sklearn.linear_model import SGDClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, make_scorer, confusion_matrix
from imblearn.under_sampling import RandomUnderSampler
from imblearn.over_sampling import SMOTE
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import StandardScaler
import pickle

filename = '../final_model.sav'
final_model = pickle.load(open(filename, 'rb'))

stopwords = nltk.corpus.stopwords.words("english")
exclusions = ["#ff", "ff", "rt"]
stopwords.extend(exclusions)
stopwords.remove("not")
stemmer = PorterStemmer()

hate_df = pd.read_csv("../dataset/Dataset1_labeled_data.csv")
tweet=hate_df.tweet

def preprocess(tweet):
    
    #remove extra spaces
    regex_pattern = re.compile(r'\s+')
    tweet_space_removed = tweet.str.replace(regex_pattern, ' ')
    
    #remove mentions(@)
    regex_patten = re.compile(r'@[\w\-]+')
    tweets = tweet_space_removed.str.replace(regex_patten, '')
    
    #remove URLs
    url_regex = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|'
                           '[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    tweets_new = tweets.str.replace(url_regex, '')
    
    #remove numbers and punctuations
    remove_punc_num = tweets_new.str.replace("[^a-zA-Z]", " ")
    
    #replace whitespaces with space
    newtweet = remove_punc_num.str.replace(r'\s+', ' ')
    
    #remove leading and trailing whitespaces
    newtweet = newtweet.str.replace(r'^\s+|\s+?$','')
    
    #lowercase
    tweets_lower = newtweet.str.lower()
    
    #tokenize
    tokenized_tweet = tweets_lower.apply(lambda x: x.split())
    
    #remove stop words
    tokenized_tweet = tokenized_tweet.apply(lambda x: [item for item in x if item not in stopwords])
    
    #stem the tweet
    tokenized_tweet = tokenized_tweet.apply(lambda x: [stemmer.stem(i) for i in x])
    
    for i in range(len(tokenized_tweet)):
        tokenized_tweet[i] = ' '.join(tokenized_tweet[i])
        tweets_pre = tokenized_tweet
        
    return tweets_pre

preprocessed_tweets = preprocess(tweet)   
hate_df['preprocessed_tweets'] = preprocessed_tweets

def tfidf_featurs(tweet):
    tweet = pd.Series(tweet)
    tfidf_vectorizer = TfidfVectorizer(ngram_range=(1, 2),max_df=1, min_df=1, max_features=10000)
    tfidf_vectorizer = TfidfVectorizer(ngram_range=(1, 2),max_df=0.75, min_df=5, max_features=10000)
    tfidf_vectorizer.fit_transform(hate_df['preprocessed_tweets'])
    tfidf_string = tfidf_vectorizer.transform(tweet)
    tfidf_array = tfidf_string.toarray()
    return np.array(tfidf_array)

sentiment_analyzer=VS()

def sentiment_analysis_string(tweet):
    sentiment = sentiment_analyzer.polarity_scores(tweet)
    features = [sentiment['neg'], sentiment['pos'], sentiment['neu'], sentiment['compound']]
    return features

def sentiment_analysis_array(tweets):
    features=[]
    for t in tweets:
        features.append(sentiment_analysis_string(t))
    return np.array(features)

def get_predictions(tweet):
    
    #convert the input string to a panda series
    tweet = pd.Series(tweet)
    
    #Get the sentiment analysis of the un-preprocessed string
    #we need to apply this function when the string is not yet pre processed in order to keep the whole meaning
    #of the sentence
    polarity_scores = sentiment_analysis_array(tweet)
    
    #preprocess the input string
    preprocessed_string = preprocess(tweet)
    
    #convert input string to a vector array
    array_tfidf = tfidf_featurs(tweet)
    
    #concatenate all the features
    final_features = np.concatenate([array_tfidf, polarity_scores], axis=1)
    
    #transform features array to a dataframe
    #final_df = pd.DataFrame(final_features)
    
    #apply final model to the input string
    prediction = final_model.predict(final_features)
    
    if prediction == 0:
        return "Hate speech"
    elif prediction == 1:
        return "Offensive Language"
    elif prediction == 2:
        return "clean"
    else:
        return "no label"   
    return prediction
