from flask import Flask, render_template,request,redirect,url_for
import json
import mysql.connector
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder 
import pandas as pd
from sklearn.naive_bayes import CategoricalNB
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import confusion_matrix

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="koreanmovieclassification"
)

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/debug")
def debug():
    return "123"

@app.route("/importdataset", methods=["POST","GET"])
def importdataset():
    if request.files:
        file = request.files["dataset"]
        data = pd.read_excel(file)
        payload=[]

        for index, row in data.iterrows():
            judul=row[0]
            stasiuntv=row[1]
            genre=row[2]
            penulis=row[3]
            direktur=row[4]
            tokohutama=row[5]
            tahundibuat=row[6]
            rating=row['rating']
            jumlahvote=row['jumlahvoter']
            totalrating=row['totalrating']
            klasifikasi=row['klasifikasi']
            payload.append((judul,stasiuntv,genre,penulis,direktur,tokohutama,tahundibuat,rating,jumlahvote,totalrating, klasifikasi))

        mydb.connect()
        cursor = mydb.cursor()
        cursor.execute("DELETE FROM dataset")
        cursor.executemany("INSERT INTO dataset VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",payload)
        mydb.commit()
        mydb.close()
        return redirect(url_for("dataset"))
    else:
        return "Please attach a file..."

@app.route("/dataset")
def dataset():

    mydb.connect()
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM dataset")
    data = cursor.fetchall()

    # {
    #       no:1,
    #       judul:"sadasd",
    #       stasiuntv:"MBS",
    #       genre:"MM",
    #       writer:"asdasd",
    #       director:"asdasddd",
    #       actor:"meme",
    #       status:"A"
    # }

    payload = []
    for index, x in enumerate(data):
        obj = {}
        obj["no"]=index+1
        obj["judul"]=x[0]
        obj["stasiuntv"]=x[1]
        obj["genre"]=x[2]
        obj["writer"]=x[3]
        obj["director"]=x[4]
        obj["actor"]=x[5]
        obj["status"]=x[10]
        payload.append(obj)

    return render_template("dataset.html", dataset=json.dumps(payload));

@app.route("/preprocessing", methods=["GET","POST"])
def preprocessing():
    if request.method=="POST":
        mydb.connect()
        cursor = mydb.cursor()
        cursor.execute("DELETE FROM preprocessing")
        cursor.execute("SELECT * FROM dataset")
        data = cursor.fetchall()
        
        labelEncoderStasiunTV=LabelEncoder()
        stasiuntv = [ x[1] for x in data]
        stasiuntv = labelEncoderStasiunTV.fit_transform(stasiuntv)

        labelEncoderGenre=LabelEncoder()
        genre = [ x[2] for x in data]
        genre = labelEncoderGenre.fit_transform(genre)


        labelEncoderWriter=LabelEncoder()
        writer = [ x[3] for x in data]
        writer = labelEncoderWriter.fit_transform(writer)

        labelEncoderDirector=LabelEncoder()
        director = [ x[4] for x in data]
        director = labelEncoderDirector.fit_transform(director)

        labelEncoderActor=LabelEncoder()
        actor = [ x[5] for x in data]
        actor = labelEncoderActor.fit_transform(actor)

        labelEncoderStatus=LabelEncoder()
        status = [ x[10] for x in data]
        status = labelEncoderStatus.fit_transform(status)

        #  {
        #       no:1,
        #       stasiuntv:"MBS",
        #       genre:"MM",
        #       writer:"asdasd",
        #       director:"asdasddd",
        #       actor:"meme",
        #       status:"A"
        #   }

        payload = []
        for x in zip(stasiuntv, genre, writer, director,actor,status):
            payload.append((int(x[0]),int(x[1]),int(x[2]),int(x[3]),int(x[4]),int(x[5])))
        cursor.executemany("INSERT INTO preprocessing VALUES (%s,%s,%s,%s,%s,%s)",payload)
        mydb.commit()
        mydb.close()
        return redirect(url_for("preprocessing"))

    mydb.connect()
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM preprocessing")
    data = cursor.fetchall()

    payload = []

    for index,value in enumerate(data):
        payload.append({
            "no":index+1,
            "stasiuntv":value[0],
            "genre":value[1],
            "writer":value[2],
            "director":value[3],
            "actor":value[4],
            "status":value[5],
        })
    return render_template("preprocessing.html",data=json.dumps(payload))


@app.route("/klasifikasi")
def klasifikasi():
    mydb.connect()
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM preprocessing")
    data = cursor.fetchall()
    X = [[x[0],x[1],x[2],x[3],x[4]] for x in data]
    y = [x[5] for x in data]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=0)
    clf = CategoricalNB()
    clf.fit(X_train,y_train)
    predicted = clf.predict(X_test)
    print(confusion_matrix(y_test,predicted))
    return render_template("klasifikasi.html")

@app.route("/pengujian")
def pengujian():
    return render_template("pengujian.html");

@app.route("/keluar")
def keluar():
    return "keluar";

if __name__=='__main__':
    app.run(debug=True)