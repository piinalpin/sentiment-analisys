from flask import render_template, request  # buat memanggil .html
from app import app
import pandas as pd
import os
import numpy as np
from .dbmodel import *
import pickle
import csv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

vectorizer = TfidfVectorizer()
naivebayes = MultinomialNB()
stemmer = StemmerFactory().create_stemmer()
remover = StopWordRemoverFactory().create_stop_word_remover()

katabaku = pd.read_csv('app/upload_data/vocab_katabaku.csv')
data_training = pd.read_csv("app/upload_data/update_dataset_raw.csv")

#############################################################################
#  PROCESS TO CREATE DATASET FOR VECTORIZER AND FIT NAIVE BAYES WITH B FILE #
#############################################################################
# X = vectorizer.fit_transform(data_training.preprocessing_result.values.astype('U'))
# naivebayes.fit(X, data_training.sentimen)
# vectorizer_file = open("app/pickle_load/vectorizer.b", "wb")
# pickle.dump(vectorizer, vectorizer_file)
# nb_file = open("app/pickle_load/nb.b", "wb")
# pickle.dump(naivebayes, nb_file)
# vectorizer_file.close()  # close it to make sure it's all been written
# nb_file.close()  # close it to make sure it's all been written


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    return render_template("upload_data.html")


@app.route('/upload_hasil', methods=['GET', 'POST'])
def upload_hasil():
    if request.method == 'POST':
        a = request.files['file']  # variabel untuk nyimpan file
        ta = request.form['ta']
        sem = request.form['semester']
        a.save(
            os.path.join('app/upload_data', 'DATA.csv'))  # wadah untuk setiap kita nge-load, hasilnya disimpan disitu
        dataku = pd.read_csv('app/upload_data/DATA.csv')
        load_vectorizer = pickle.load(open("app/pickle_load/vectorizer.b", "rb"), encoding='latin1')
        load_naivebayes = pickle.load(open("app/pickle_load/nb.b", "rb"), encoding='latin1')
        pegawai = [str(x) for x in list(dataku["pegawai_id_pegawai"])]
        ampu = [str(x) for x in list(dataku["ampu_id_ampu"])]
        baku = [x for x in katabaku["kata_baku"]]

        new_data = []
        save_index = []

        def unique(listq):
            unique_list = []
            for x in listq:
                unique_list.append(x)
            return unique_list

        listStemUji = []
        for low in dataku.answer:
            lowerku = low.lower()
            textStemmed = stemmer.stem(lowerku)
            textClean = remover.remove(textStemmed)
            n = 0
            for i in katabaku["vocabulary"]:
                if textClean == i:
                    textClean = baku[n]
                n += 1
            listStemUji.append(textClean)

        data_sentimen = []

        tfidf = load_vectorizer.transform(data_training.preprocessing_result.astype('U'))
        for i in tfidf:
            sentiment = load_naivebayes.predict(i)
            data_sentimen.append(sentiment)
        data_sentimen
        for i in range(0, len(dataku)):
            index = pegawai[i] + ',' + ampu[i]
            save_index.append(index)
            new_data.append([index, [data_sentimen[i]]])
        new_data = unique(new_data)

        clean_index = list(set(save_index))
        total = 0
        y = 0
        data_gue = []
        sumPositive = 0
        sumNegative = 0
        sumNetral = 0
        sumAll = 0
        totalPrecentPositive = 0
        totalPrecentNetral = 0
        totalPrecentNegative = 0
        for i in clean_index:
            for j in new_data:
                if str(i) == j[0]:
                    if np.int_(j[1]) == 0:
                        sumNegative += 1
                    elif np.int_(j[1]) == 2:
                        sumPositive += 1
                    elif np.int_(j[1]) == 1:
                        sumNetral += 1
                    sumAll += 1
            precentNegative = round((float(sumNegative) / float(sumAll)) * 100, 2)
            precentPositive = round((float(sumPositive) / float(sumAll)) * 100, 2)
            precentNetral = round((float(sumNetral) / float(sumAll)) * 100, 2)
            totalPrecentPositive += precentPositive
            totalPrecentNetral += precentNetral
            totalPrecentNegative += precentNegative
            data_gue.append([i, precentPositive, precentNetral, precentNegative])
        rataPOS = round(float(totalPrecentPositive) / len(clean_index), 2)
        rataNET = round(float(totalPrecentNetral) / len(clean_index), 2)
        rataNEG = round(float(totalPrecentNegative) / len(clean_index), 2)

        data_final = []
        for i in data_gue:
            n = i[0].split(',')
            data_final.append([n[0], n[1], i[1], i[2], i[3]])
        print(data_final)
        framegue = pd.DataFrame.from_dict(data_final)
        framegue.columns = ['Id Dosen', 'Id Mata Kuliah', 'Sentimen Positif (%)', 'Sentimen Netral (%)',
                            'Sentimen Negatif (%)']

        tahun_ajaran = str(ta) + '_' + str(sem)
        namaFile = 'app/db/' + str(ta) + '_' + str(sem) + '.csv'
        try:
            sentiment_obj = Sentiment(tahun_ajaran=tahun_ajaran, positive=rataPOS, neutral=rataNET, negative=rataNEG)
            sentiment_obj.save()
        except Exception as e:
            print(e)
        framegue.to_csv(namaFile, quoting=csv.QUOTE_ALL, sep=',', escapechar='"', mode='w', header=True, index=False)
    return render_template('hasil_upload.html', tables=[framegue.to_html(classes='table table-bordered')])
    # return "MAVERICK"


@app.route('/', methods=['GET', 'POST'])
def Index():
    return render_template('index.html')


@app.route('/hasil_analisa', methods=['GET', 'POST'])
def hasil():
    sentiment_obj = Sentiment.getAll();
    tab = []
    nfile = []
    for obj in sentiment_obj:
        nf = 'app/db/' + str(obj.tahun_ajaran) + '.csv'
        nfile.append(nf)
        tab.append(obj.tahun_ajaran)
    dtab = []
    for i in nfile:
        loadDB = pd.read_csv(i)
        dtab.append(loadDB)
    dftab = []
    for i in dtab:
        a = pd.DataFrame(i)
        a.columns = ['Id Dosen', 'Id Mata Kuliah', 'Sentimen Positif (%)', 'Sentimen Netral (%)',
                     'Sentimen Negatif (%)']
        dftab.append(a)
    print(dtab)
    return render_template('hasil_analisa.html', tab=tab, dftab=dftab, n=len(tab))


@app.route('/grafik', methods=['GET', 'POST'])
def Grafik():
    sentiment_obj = Sentiment.getAll();
    tabel = []
    for obj in sentiment_obj:
        tabel.append([obj.tahun_ajaran, obj.positive, obj.neutral, obj.negative])
    tabel
    year = []
    pos = []
    net = []
    neg = []
    for i in tabel:
        year.append(i[0])
        pos.append(i[1])
        net.append(i[2])
        neg.append(i[3])
    return render_template('grafik.html', year=year, pos=pos, net=net, neg=neg, n=len(year))
