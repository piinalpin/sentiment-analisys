from flask import render_template, request #buat memanggil .html
from app import app
from openpyxl import load_workbook
import pandas as pd
import os
import numpy as np
import dbmodel as database
import xlrd
import json
import plotly
import string
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

vectorizer = TfidfVectorizer()
naivebayes = MultinomialNB()
stemmer = StemmerFactory().create_stemmer()
remover = StopWordRemoverFactory().create_stop_word_remover()


@app.route('/upload', methods= ['GET','POST'])
def upload():
    return render_template("upload_data.html")

@app.route('/upload_hasil', methods= ['GET','POST'])
def upload_hasil():
    if request.method == 'POST':
        a=request.files['file'] #variabel untuk nyimpan file
        b=request.form['sheet']

        a.save(os.path.join('app/upload_data', 'DATA.xlsx')) #wadah untuk setiap kita nge-load, hasilnya disimpan disitu
        wb = load_workbook(filename='app/upload_data/DATA.xlsx')
        sheet_ranges = wb[b]
        data = pd.DataFrame(sheet_ranges.values)
        mylist = []
        mylist.append(data[0].values.tolist())
        load_vectorizer = pickle.load(open("app/upload_data/vectorizer.b", "rb"))
        load_naivebayes = pickle.load(open("app/upload_data/nb.b", "rb"))
        listStem = []
        for i in mylist:
            for j in i:
                datalow = j.lower()
                a = datalow.encode("ascii","ignore")
                textStemmed = stemmer.stem(a)
                textClean = remover.remove(textStemmed)
                listStem.append(textClean)
        sumPositive = 0
        sumNegative = 0
        sumAll = 0
        tfidf = load_vectorizer.transform(listStem)
        for i in tfidf:
            sentiment = load_naivebayes.predict(i)
            if sentiment == 0:
                sumNegative += 1
            elif sentiment == 1:
                sumPositive += 1
            sumAll += 1
        precentNegative = round((float(sumNegative)/float(sumAll))*100,2)
        precentPositive = round((float(sumPositive)/float(sumAll))*100, 2)
        strNegative = "Total Sentimen Negatif : " + str(sumNegative)
        strPositive = "Total Sentimen Positif : " + str(sumPositive)
        strAll = "Total Seluruh Sentimen : " + str(sumAll)
        strPrecentNegative = "Prosentase Sentimen Negatif : " + str(precentNegative) + "%"
        strPrecentPositive = "Prosentase Sentimen Positif : " + str(precentPositive) + "%"
    return render_template('hasil_upload.html', strNegative=strNegative, strPositive=strPositive, strAll=strAll, strPrecentNegative=strPrecentNegative, strPrecentPositive=strPrecentPositive)
    # return "MAVERICK"

@app.route('/', methods=['GET','POST'])
def Index():
    data_training = pd.read_csv("app/upload_data/id-preprocess.csv")
    X = vectorizer.fit_transform(data_training.preprocessing_result)
    naivebayes.fit(X, data_training.Sentiment)
    vectorizer_file = open("app/upload_data/vectorizer.b", "wb")
    pickle.dump(vectorizer, vectorizer_file)
    nb_file = open("app/upload_data/nb.b", "wb")
    pickle.dump(naivebayes, nb_file)
    vectorizer_file.close() # close it to make sure it's all been written
    nb_file.close() # close it to make sure it's all been written
    return render_template('index.html')    




