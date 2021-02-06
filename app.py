from flask import Flask, render_template,request,redirect,url_for,session
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

app.secret_key="nuhaaaaaa"

@app.route("/",methods=["POST","GET"])
def public_classification():
    if request.method=="POST":

        stasiuntv_ = request.form["stasiuntv"]
        genre_ = request.form["genre"]
        penulis_ = request.form["penulis"]
        direktur_ = request.form["direktur"]
        tokohutama_ = request.form["tokohutama"]
        
        mydb.connect()
        cursor = mydb.cursor()
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

        s = labelEncoderStasiunTV.transform([stasiuntv_])[0]
        g = labelEncoderGenre.transform([genre_])[0]
        p = labelEncoderWriter.transform([penulis_])[0]
        d =labelEncoderDirector.transform([direktur_])[0]
        t =labelEncoderActor.transform([tokohutama_])[0]

        cursor.execute("SELECT * FROM preprocessing WHERE preprocessing.tahundibuat REGEXP '(2005|2006|2007|2008|2009|2010|2011|2012|2013|2014|2015|2016|2017|2018|2019|2020)'")
        training = cursor.fetchall()
        X = [[x[0],x[1],x[2],x[3],x[4]] for x in training]
        y = [x[5] for x in training]
        clf = CategoricalNB()
        clf.fit(X,y)

        hasil = labelEncoderStatus.inverse_transform([clf.predict([[s,g,p,d,t]])[0]])[0]
        mydb.close()

        return render_template("public_classification.html",hasil=hasil)
    mydb.connect()
    cursor=mydb.cursor()
    
    cursor.execute("SELECT DISTINCT(stasiuntv) FROM dataset");
    stasiuntv = [x[0] for x in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT(genre) FROM dataset")
    genre = [x[0] for x in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT(penulis) FROM dataset")
    penulis = [x[0] for x in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT(direktur) FROM dataset")
    direktur = [x[0] for x in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT(tokohutama) FROM dataset")
    tokohutama = [x[0] for x in cursor.fetchall()]


    cursor.close()
    mydb.close()
    return render_template("public_Classification.html", genre=genre,stasiuntv=stasiuntv,penulis=penulis,direktur=direktur,tokohutama=tokohutama)



@app.route("/login", methods=["POST","GET"])
def index():
    if 'admin' in session:
        return redirect(url_for("dashboard"))
    if request.method=="POST":
        email = request.form["email"]
        password = request.form["password"]
        if len(email)==0 or len(password)==0:
            return render_template("index.html",error="Email atau password tidak boleh kosong!")
        else:
            mydb.connect()
            cursor = mydb.cursor(buffered=True)

            cursor.execute("SELECT * FROM admin WHERE email=%s",(email,))
            account = cursor.fetchone()


            if account==None:
                cursor.close()
                mydb.close()
                return render_template("index.html",error="Email tidak ditemukan!")
            else:
                u = account[1]
                p = account[2]
                cursor.close()
                mydb.close()
                if u==email and p==password:
                    session["admin"]=True
                    return redirect(url_for("dashboard"))
                else:
                    return render_template("index.html",error="Login gagal!")
    return render_template("index.html")

@app.route("/dashboard", methods=["POST","GET"])
def dashboard():
    if "admin" not in session:
        return redirect(url_for("index"))

    mydb.connect()
    cursor=mydb.cursor()
    
    cursor.execute("SELECT DISTINCT(stasiuntv) FROM dataset");
    stasiuntv = [x[0] for x in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT(genre) FROM dataset")
    genre = [x[0] for x in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT(penulis) FROM dataset")
    penulis = [x[0] for x in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT(direktur) FROM dataset")
    direktur = [x[0] for x in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT(tokohutama) FROM dataset")
    tokohutama = [x[0] for x in cursor.fetchall()]


    cursor.close()
    mydb.close()
    return render_template("dashboard.html", genre=genre,stasiuntv=stasiuntv,penulis=penulis,direktur=direktur,tokohutama=tokohutama)


@app.route("/importdataset", methods=["POST","GET"])
def importdataset():
    if "admin" not in session:
        return redirect(url_for("index"))
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
    if "admin" not in session:
        return redirect(url_for("index"))
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
    if "admin" not in session:
        return redirect(url_for("index"))
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

        tahundibuat = [ x[6] for x in data]

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
        for x in zip(stasiuntv, genre, writer, director,actor,status,tahundibuat):
            payload.append((int(x[0]),int(x[1]),int(x[2]),int(x[3]),int(x[4]),int(x[5]),x[6]))
        cursor.executemany("INSERT INTO preprocessing VALUES (%s,%s,%s,%s,%s,%s,%s)",payload)
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
    if "admin" not in session:
        return redirect(url_for("index"))
    mydb.connect()
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM preprocessing WHERE preprocessing.tahundibuat REGEXP '(2005|2006|2007|2008|2009|2010|2011|2012|2013|2014|2015|2016|2017|2018|2019)'")
    training = cursor.fetchall()
    X = [[x[0],x[1],x[2],x[3],x[4]] for x in training]
    y = [x[5] for x in training]
    # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=0)
    clf = CategoricalNB()
    clf.fit(X,y)
    cursor.execute("SELECT * FROM preprocessing WHERE preprocessing.tahundibuat REGEXP '(2020)'")
    testing = cursor.fetchall()
    X_test = [[x[0],x[1],x[2],x[3],x[4]] for x in testing]
    y_test = [x[5] for x in testing]
    predicted = clf.predict(X_test)
    payload = []
    for index,x in enumerate(X_test):
        arr = x
        arr.append(y[index])
        payload.append({
            "no":index+1,
            "stasiuntv":arr[0],
            "genre":arr[1],
            "writer":arr[2],
            "director":arr[3],
            "actor":arr[4],
            "status":arr[5],
        })
    #print(confusion_matrix(y_test,predicted))
    return render_template("klasifikasi.html", data=json.dumps(payload))

@app.route("/pengujian")
def pengujian():
    if "admin" not in session:
        return redirect(url_for("index"))
    mydb.connect()
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM preprocessing WHERE preprocessing.tahundibuat REGEXP '(2005|2006|2007|2008|2009|2010|2011|2012|2013|2014|2015|2016|2017|2018|2019)'")
    training = cursor.fetchall()
    X = [[x[0],x[1],x[2],x[3],x[4]] for x in training]
    y = [x[5] for x in training]
    # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=0)
    clf = CategoricalNB()
    clf.fit(X,y)
    cursor.execute("SELECT * FROM preprocessing WHERE preprocessing.tahundibuat REGEXP '(2020)'")
    testing = cursor.fetchall()
    X_test = [[x[0],x[1],x[2],x[3],x[4]] for x in testing]
    y_test = [x[5] for x in testing]
    predicted = clf.predict(X_test)
    payload = []
    for index,x in enumerate(X_test):
        arr = x
        arr.append(y[index])
        payload.append({
            "no":index+1,
            "stasiuntv":arr[0],
            "genre":arr[1],
            "writer":arr[2],
            "director":arr[3],
            "actor":arr[4],
            "status":arr[5],
        })
    hasil = confusion_matrix(y_test,predicted)
    akurasi = (hasil[0][0]+hasil[1][1])/(hasil[0][0]+hasil[0][1]+hasil[1][0]+hasil[1][1])
    
    return render_template("pengujian.html",hasil=hasil,akurasi=round(akurasi*100));

@app.route("/keluar")
def keluar():
    session.pop("admin",None)
    return redirect(url_for("index"))

if __name__=='__main__':
    app.run(debug=True)