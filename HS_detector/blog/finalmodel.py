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
#nltk.download('vader_lexicon')
from textstat.textstat import textstat
from wordcloud import WordCloud
#%matplotlib inline
from matplotlib import pyplot as plt

from PIL import Image
import cv2
from matplotlib import pyplot as plt
import pytesseract
# from PIL import Image
# from gensim.test.utils import common_texts
# import seaborn
# from sklearn.metrics import confusion_matrix
# from sklearn.model_selection import train_test_split
# from sklearn.linear_model import LogisticRegression
# from sklearn.svm import LinearSVC
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.naive_bayes import GaussianNB
# from sklearn.neighbors import KNeighborsClassifier
# from sklearn import svm
# from sklearn.linear_model import SGDClassifier
# from sklearn.tree import DecisionTreeClassifier
# from sklearn.metrics import classification_report
# from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, make_scorer, confusion_matrix
# from imblearn.under_sampling import RandomUnderSampler
# from imblearn.over_sampling import SMOTE
# from sklearn.pipeline import Pipeline
# from sklearn.model_selection import GridSearchCV
# from sklearn.model_selection import StratifiedKFold
# from sklearn.metrics import confusion_matrix
# from sklearn.preprocessing import StandardScaler
import pickle
sentiment_analyzer=VS()

filename = '../final_model.pkl'
final_model = pickle.load(open(filename, 'rb'))

stopwords = nltk.corpus.stopwords.words("english")
exclusions = ["#ff", "ff", "rt"]
stopwords.extend(exclusions)
stopwords.remove("not")
stemmer = PorterStemmer()

hate_df = pd.read_csv("../dataset/New_dataset.csv")
tweet=hate_df.tweet

#tf-idf
def tfidf_featurs(tweet):
    tweet = pd.Series(tweet)
    tfidf_vectorizer = TfidfVectorizer(ngram_range=(1, 2),max_df=1, min_df=1, max_features=10000)
    tfidf_vectorizer = TfidfVectorizer(ngram_range=(1, 2),max_df=0.75, min_df=5, max_features=10000)
    tfidf_vectorizer.fit_transform(hate_df['preprocessed_tweets'].values.astype('U'))
    tfidf_string = tfidf_vectorizer.transform(tweet)
    tfidf_array = tfidf_string.toarray()
    return tfidf_array

#polarity scores
def sentiment_analysis_string(tweet):
    sentiment = sentiment_analyzer.polarity_scores(tweet)
    features = [sentiment['neg'], sentiment['pos'], sentiment['neu'], sentiment['compound']]
    return features

def sentiment_analysis_array(tweets):
    features=[]
    for t in tweets:
        features.append(sentiment_analysis_string(t))
    return np.array(features)

#binarize image
def binarize(image):
    gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) #convert to grayscale
    thresh, im_bw = cv2.threshold(gray_img, 200, 250, cv2.THRESH_BINARY) #convert to b&w
    return im_bw

#remove noise
def noise_removal(image):
    kernal = np.ones((1, 1), np.uint8)
    image = cv2.dilate(image, kernal, iterations=1)
    kernal = np.ones((1,1), np.uint8)
    image = cv2.erode(image, kernal, iterations=1)
    image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernal)
    #image = cv2.medianBlur(image, 3)
    return (image)

#remove borders
def remove_borders(image):
    contours, heiarchy = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cntsSorted = sorted(contours, key=lambda x:cv2.contourArea(x))
    cnt = cntsSorted[-1]
    x, y, w, h = cv2.boundingRect(cnt)
    crop = image[y:y+h, x:x+w]
    return (crop)

#get text from image
def ocr(image):
    img = cv2.imread(image)
    binary = binarize(img)
    denoised = noise_removal(binary)
    b_removed = remove_borders(denoised)
    
    ocr_result = pytesseract.image_to_string(img)
    processed_text = ' '.join(ocr_result.split())
    return processed_text


#get the predictions
def get_predictions(user_input):
    
    #convert the input string to a panda series
    pd_input = pd.Series(user_input)
    
    #Get the sentiment analysis of the un-preprocessed string
    #we need to apply this function when the string is not yet pre processed in order to keep the whole meaning
    #of the sentence
    polarity_scores = sentiment_analysis_array(pd_input)
     
    #convert input string to a vector array
    array_tfidf = tfidf_featurs(pd_input)
    
    #concatenate all the features
    final_features = np.concatenate([array_tfidf, polarity_scores], axis=1)
    final_f = np.array(final_features)
    
    #transform features array to a dataframe
    final_df = pd.DataFrame(final_f)
    
    #apply final model to the input string
    prediction = final_model.predict(final_df)
    
    # if prediction == 0:
    #     return "Hate speech"
    # elif prediction == 1:
    #     return "Offensive Language"
    # elif prediction == 2:
    #     return "clean"
    # else:
    #     return "no label"   
    return prediction


