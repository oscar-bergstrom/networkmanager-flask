from flask import Flask, render_template, request
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


@app.route("/interfaces/<interface_id>")
def interface(interface_id):
    try:
        info = nmcli.get_device_info(interface_id)
    except OSError as e:
        info = {"ERROR": e.__str__()}
    return render_template("interface.html", interface=info)


@app.route("/interfaces/<interface_id>/list")
def interface_list(interface_id):
    networks = nmcli.scan_networks(interface_id)
    return render_template("list.html", interface=interface_id, networks=networks)


@app.route("/connections/add")
def add_wifi_connection():
    devices = nmcli.get_devices()
    interfaces_ = [device.device for device in devices if device.type == "wifi"]

    args = request.args
    return render_template("connect.html",
                           interfaces=interfaces_,
                           ssid=args.get("ssid", ""),
                           selected_interface=args.get("interface", ""))
