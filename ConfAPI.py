#!/usr/bin/python3.6
# coding: utf8

import os,glob
import random
import base64
from asterisk.ami import AMIClient
from asterisk.ami import SimpleAction
from gevent.pywsgi import WSGIServer
from flask import Flask,render_template,request


app = Flask(__name__)


@app.route('/asterisk/conf/api/v0.0.1/start')
def action():
    room = request.args.get('room')
    numbers = request.args.get('numbers')
    numbers = numbers.split(";")
    message = "Conference room - " + room + ". Called Numbers/Extensions - "

    serverip = "127.0.0.1"
    serverport = 5038
    username = "AMIUser"
    secret = "AMIPass"
    prio = 1
    context = "api-conf"
    d_number = room


    for number in numbers:
        message = message + " " + number
        extension = number
        channel = "local/" + number + "@from-internal"

        client = AMIClient(address=serverip, port=serverport)
        client.login(username=username, secret=secret)

        action = SimpleAction(
            'Originate',
            Channel=channel,
            Exten=d_number,
            Priority=prio,
            Context=context,
        )

        client.send_action(action)

    return render_template('action.html',n = message)


@app.route('/asterisk/conf/api/v0.0.1/rooms')
def rooms():
    movepath = 'find /usr/scripts/python3/templates/rooms_* -type f -mmin +1 -delete'
    move = os.system(movepath)
    roomkey = random.uniform(0, 100)
    roomcommand = f'/usr/bin/grep "confbridge" /etc/asterisk/extensions* | /usr/bin/grep -v "&" | sed "s|.*,||" | /usr/bin/ansi2html > /usr/scripts/python3/templates/rooms_{roomkey}.html'
    roomlist = os.system(roomcommand)
    return render_template(f'rooms_{roomkey}.html')


@app.route('/asterisk/conf/api/v0.0.1/online-rooms')
def online():
    removepath = '/usr/bin/find /usr/scripts/python3/templates/conferences_* -type f -mmin +1 -delete'
    remove = os.system(removepath)
    key = random.uniform(0, 100)
    getonlineconf = f'/usr/sbin/asterisk -rx "confbridge list"| /usr/bin/ansi2html > /usr/scripts/python3/templates/conferences_{key}.html'
    onlineconflist = os.system(getonlineconf)
    return render_template(f'conferences_{key}.html')


@app.route('/asterisk/conf/api/v0.0.1/about')
def about():
    return render_template('about.html')


if __name__ == "__main__":
    http_server = WSGIServer(('', 1098), app)
    http_server.serve_forever()

