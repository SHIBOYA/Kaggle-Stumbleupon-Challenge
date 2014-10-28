#import
import numpy as np
from sklearn import metrics,preprocessing,cross_validation
from sklearn.feature_extraction.text import TfidfVectorizer
import os
import json
import pickle
import sklearn.linear_model as lm
import sklearn.svm as sm
import pandas as p
from nltk.corpus import stopwords
from nltk.tokenize.punkt import PunktWordTokenizer
from nltk.stem.snowball import SnowballStemmer

#initialise stemmer
stemmer = SnowballStemmer("english")

def stem_tokens(tokens, stemmer):
    stemmed = []
    for item in tokens:
        stemmed.append(stemmer.stem(item))
    return stemmed

def tokenize(text):
    tokens = PunktWordTokenizer().tokenize(text)
    stems = stem_tokens(tokens, stemmer)
    return stems


def main():
  #load data
  print "loading data.."
  traindata = list(np.array(p.read_table('train.tsv'))[:,2])
  testdata = list(np.array(p.read_table('test.tsv'))[:,2])
  y = np.array(p.read_table('train.tsv'))[:,-1]

  #initialise Linear SVM Classifier
  rd = sm.LinearSVC(penalty='l2', dual=True, tol=0.0001, 
                   C=1, fit_intercept=True, intercept_scaling=1.0, 
                   class_weight=None, random_state=None)

  lentrain = len(traindata)

  #initialise Tf-Idf Vectorizer
  tfv = TfidfVectorizer(min_df=3, max_features=None, strip_accents='unicode',  
                        analyzer='word',token_pattern=r'\w{1,}',ngram_range=(1, 2), 
                        use_idf=1,smooth_idf=1,sublinear_tf=1,
                        #stop_words=stopwords.words('english'),
                        tokenizer=tokenize)


  X_all = traindata + testdata
  print "fitting pipeline"
  tfv.fit(X_all)
  print "transforming data"
  X_all = tfv.transform(X_all)
  X = X_all[:lentrain] 
  X_test = X_all[lentrain:]

  #predict CV score
  print "20 Fold CV Score: ", np.mean(cross_validation.cross_val_score(rd, X, y, cv=20, scoring='roc_auc'))

  print "training on full data"
  rd.fit(X,y)
  pred = rd.predict(X_test)
  testfile = p.read_csv('test.tsv', sep="\t", na_values=['?'], index_col=1)
  pred_df = p.DataFrame(pred, index=testfile.index, columns=['label'])
  pred_df.to_csv('benchmark.csv')
  print "submission file created.."

if __name__=="__main__":
  main()
