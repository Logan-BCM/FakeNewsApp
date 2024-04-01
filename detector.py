#! /usr/bin/env python3

import os
import re
import pickle
import numpy as np
import pandas as pd

import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

from sklearn.ensemble import VotingClassifier
from sklearn.metrics import accuracy_score, recall_score, precision_score, f1_score
from sklearn.naive_bayes import ComplementNB, GaussianNB, MultinomialNB

from tensorflow.keras.preprocessing.text import one_hot
from tensorflow.keras.preprocessing.sequence import pad_sequences


BASE_DIRR = os.path.dirname(os.path.abspath(__file__))

get_path_for = lambda x: os.path.join(BASE_DIRR, f"assets/{x}")

voc_size = 5000
sent_length = 20

def save_pickle(filename, data):
    pickle_path = get_path_for(filename)

    file = open(pickle_path, "wb")
    pickle.dump(data, file)
    file.close()


def load_pickle(filename):
    pickle_path = get_path_for(filename)

    file = open(pickle_path, "rb")
    data = pickle.load(file)
    file.close()
    return data


def calculate_scores(y_test, y_pred):
    print("Accuracy Score:", accuracy_score(y_test,y_pred))
    print("Recall Score:", recall_score(y_test, y_pred))
    print("Precision Score:", precision_score(y_test, y_pred))
    print("F1 Score:", f1_score(y_test, y_pred))
    return {
        "accuracy_score": accuracy_score(y_test,y_pred),
        "recall_score": recall_score(y_test, y_pred),
        "precision_score": precision_score(y_test, y_pred),
        "f1_score": f1_score(y_test, y_pred)
    }


def train_model(filename):
    nltk.download("stopwords")

    dataset_path = get_path_for(filename)

    train = pd.read_csv(dataset_path)
    train_data = train.copy()
    train_data=train_data.dropna()

    ## Get the Independent Features
    X=train_data.drop("label",axis=1)

    ## Get the Dependent features
    y=train_data["label"]

    messages=X.copy()
    messages.reset_index(inplace=True)

    ### Dataset Preprocessing
    print("Started dataset preprocessing")
    ps = PorterStemmer()
    corpus = []
    
    for i in range(0, len(messages)):
        # review = re.sub("[^a-zA-Z]", " ", messages["title"][i])
        review = re.sub("[^a-zA-Z]", " ", messages["text"][i])
        review = review.lower()
        review = review.split()
        
        review = [ps.stem(word) for word in review if not word in stopwords.words("english")]
        review = " ".join(review)
        corpus.append(review)

    print("\nDone dataset preprocessing")
    
    save_pickle("corpus.pickle", corpus)
    print("saved corpus")

    print("One hot rep")
    onehot_repr=[one_hot(words,voc_size)for words in corpus]

    embedded_docs=pad_sequences(onehot_repr,padding="pre",maxlen=sent_length)

    X_final=np.array(embedded_docs)
    y_final=np.array(y)

    # Create different Naive Bayes classifiers
    nb_gaussian = GaussianNB()
    nb_multinomial = MultinomialNB()
    nb_complement = ComplementNB()

    # Combine classifiers into a VotingClassifier
    voting_classifier = VotingClassifier(estimators=[
        ("gaussian", nb_gaussian),
        ("multinomial", nb_multinomial),
        ("complement", nb_complement),
    ], voting="hard")

    # Train the VotingClassifier
    voting_classifier.fit(X_final, y_final)

    save_pickle("nb_model.pickle", voting_classifier)
    print("Model saved")

    return voting_classifier


def porter_stemmer(text):
    ps = PorterStemmer()
    review = re.sub('[^a-zA-Z]', ' ', text)
    review = review.lower()
    review = review.split()

    review = [ps.stem(word) for word in review if not word in stopwords.words('english')]
    review = ' '.join(review)
    return review


def predict(content):
    model = load_pickle("nb_model.pickle")

    review = porter_stemmer(content)
    onehot_repr = one_hot(review, voc_size)
    embedded_docs = pad_sequences([onehot_repr], padding='pre', maxlen=sent_length)

    pred = model.predict(embedded_docs)

    return pred[0] == 1


if __name__ == "__main__":
    train_model("datasets/train.csv")
