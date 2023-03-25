from flask import Flask, render_template
from markupsafe import escape
from datetime import datetime

import nmcli

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html", utc_dt=datetime.utcnow())


@app.route("/connections")
def connections():
    con = nmcli.get_connections()
    print("con:", con)
    return render_template("connections.html", connections=con)


@app.route("/connections/<con>")
def connection(con):
    try:
        info = nmcli.get_connection_info(con)
    except OSError as e:
        info = {"ERROR": e.__str__()}
    return render_template("connection.html", connection=info)


@app.route("/interfaces")
def interfaces():
    return render_template("interfaces.html", interfaces=nmcli.get_devices())

