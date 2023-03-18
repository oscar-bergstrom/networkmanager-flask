from flask import Flask, render_template
from markupsafe import escape
from datetime import datetime


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html", utc_dt=datetime.utcnow())


@app.route("/name/<name>")
def hello(name):
    return f"Hello, {escape(name)}!"


@app.route("/local")
def local_list():
    with open("/proc/cpuinfo") as f:
        return f"<p>{f.read()}</p>"

