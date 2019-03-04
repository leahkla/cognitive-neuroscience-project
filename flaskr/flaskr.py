import os
import json
import pandas as pd
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure, show, output_file
from bokeh.embed import components
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, session
from flask_session import Session

from DatabaseClient import DatabaseClient


#SESSION_TYPE = 'redis'
#app.config.from_object(__name__)
app = Flask(__name__)
app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = 'super secret key'
sess = Session()

d = DatabaseClient()

@app.route('/')
def index():
    if session.get('username'):
        return render_template('frontend/index.html')
    else:
        return redirect(url_for("login"))

@app.route('/login')
def login():
    return render_template('frontend/login.html')

@app.route('/save', methods=['POST'])
def save():
    if not session.get('username'):
        return "Error: username not set"
    else:
        d.insert_post({"timestamp":request.form.get('timestamp'), "value": request.form.get('value'), "videoname": request.form.get('videoname'), "username": session['username']})
        return "Saving completed"


@app.route('/submit_username', methods=['POST'])
def submit_username():
    print(request.form.get('username'))
    session['username'] = request.form.get('username')
    return redirect(url_for('index'))

@app.route('/researcher_view', methods=['GET'])
def chart():
    # mock data:
    data2 = {"objects": [{"timestamp": "1", "value": "-0.5", "videoname": "dog video"},
                    {"timestamp": "3.5", "value": "1", "videoname": "cat video"},
                    {"timestamp": "5", "value": "-1", "videoname": "rat video"},
                    {"timestamp": "6.5", "value": "0.7", "videoname": "capybara video"},
                    {"timestamp": "10.2", "value": "0.25", "videoname": "parrot video"},
                    {"timestamp": "20.5", "value": "0.57", "videoname": "lizard video"},
                    {"timestamp": "22.8", "value": "0.91", "videoname": "another cat video"}]}
    # commented original calling-json-function:
    #data = d.collect_posts()
    jsonData2 = json.loads(json.dumps(data2)) # type == dict
    df = pd.DataFrame(jsonData2)
    data_valence = df.objects.apply(lambda x: pd.Series(x))

    TOOLS = 'save,pan,box_zoom,reset,wheel_zoom,hover'
    p = figure(title="Valence ratings by timestamp", y_axis_type="linear", x_range=(0, 23), y_range=(-1, 1), plot_height = 400,
           tools = TOOLS, plot_width = 900)
    p.xaxis.axis_label = 'Timestamp (seconds)'
    p.yaxis.axis_label = 'Valence rating'
    p.line(data_valence.timestamp, data_valence.value,line_color="purple", line_width = 3)

    source = ColumnDataSource(data={
    'timestamp': data_valence.timestamp,
    'value': data_valence.value,
    'videoname': data_valence.videoname})

    p.select_one(HoverTool).tooltips = [
    ('timestamp', '@x'),
    ('Rating of valence', '@y')
    ]

    script, div = components(p)
    return render_template("frontend/index2.html", the_div=div, the_script=script)



@app.route('/collect_data')
def collect_data():
    posts = d.collect_posts()
    collected = []
    for p in posts:
        if p['_id']:
            del p['_id']
        collected.append(p)
    return json.dumps({"objects": collected})

@app.route('/delete_all')
def delete_data():
    d.delete_many({})
    return "All items deleted :)"


@app.route('/<path:path>')
def static_file(path):
    return app.send_static_file(path)
