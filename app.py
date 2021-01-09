from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/dataset")
def dataset():
    return render_template("dataset.html");

if __name__=='__main__':
    app.run(debug=True)