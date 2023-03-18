from flask import Flask, render_template
from markupsafe import escape
from datetime import datetime


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html", utc_dt=datetime.utcnow())


@app.route("/connections")
def connections():
    return render_template("connections.html")


@app.route("/interfaces")
def interfaces():
    return render_template("interfaces.html")

