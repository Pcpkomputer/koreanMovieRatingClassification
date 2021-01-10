from flask import Flask, render_template
import json
import mysql.connector

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

@app.route("/preprocessing")
def preprocessing():
    return render_template("preprocessing.html");

@app.route("/klasifikasi")
def klasifikasi():
    return render_template("klasifikasi.html");

@app.route("/pengujian")
def pengujian():
    return render_template("pengujian.html");

@app.route("/keluar")
def keluar():
    return "keluar";

if __name__=='__main__':
    app.run(debug=True)