from flask import Flask, redirect, render_template, request, url_for
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
    return render_template("connections.html", connections=con)


@app.route("/connections/<con>")
def connection(con):
    try:
        info = nmcli.get_connection_info(con)
    except OSError as e:
        info = {"ERROR": e.__str__()}
    return render_template("connection.html", connection=info)


@app.route("/connections/<con>/delete")
def delete_connection(con):
    try:
        nmcli.delete_connection(con)
    except IOError:
        pass

    return redirect(url_for("connections"))


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


@app.route("/connections/add", methods=["GET", "POST"])
def add_wifi_connection():
    if request.method == "POST":

        ssid = request.form.get("ssid")
        psk = request.form.get("psk")
        device = request.form.get("interface")
        if device == "All":
            device = None

        if ssid and psk:
            try:
                nmcli.add_wifi(ssid, psk, device=device)
                return redirect(url_for("connection", con=ssid))
            except Exception as e:
                return e.__str__()

    # Handling
    devices = nmcli.get_devices()
    interfaces_ = [device.device for device in devices if device.type == "wifi"]

    return render_template("connect.html",
                           interfaces=interfaces_,
                           ssid=request.args.get("ssid", ""),
                           selected_interface=request.args.get("interface", ""))

