import os
import json
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

from DatabaseClient import DatabaseClient

app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file , flaskr.py

app.config.from_envvar('FLASKR_SETTINGS', silent=True)
d = DatabaseClient()

@app.route('/')
def index():
    return render_template('frontend/index.html')

@app.route('/save', methods=['POST'])
def save():
    t = request.form.get('timestamp')
    v = request.form.get('value')
    print(v)
    videoname = request.form.get('videoname')
    d.insert_post({"timestamp":t, "value": v, "videoname": videoname})
    return "Saving completed"

@app.route('/collect_data')
def collect_data():
    posts = d.collect_posts()
    collected = []
    for p in posts:
        del p['_id']
        collected.append(p)
    return json.dumps({"objects": collected})


@app.route('/<path:path>')
def static_file(path):
    return app.send_static_file(path)
