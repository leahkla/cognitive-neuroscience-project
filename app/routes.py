"""
This file contains the routes, i.e. the functions to be executed when a page
(like "/" or "/index") is accessed in the browser.
"""

import json
import pandas as pd

from flask import request, redirect, url_for, render_template, session

from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure
from bokeh.embed import components

# from scipy.interpolate import CubicSpline
# from scipy.interpolate import spline
# from scipy.interpolate import interp1d

from app import app
from .database_client import DatabaseClient
from .helper_functions import collect_mongodbobjects


d = DatabaseClient()

@app.route('/index')
@app.route('/')
def index():
    """
    Display the main page.
    :return: Main webpage
    """
    if session.get('username'):
        return render_template('frontend/index.html')
    else:
        return redirect(url_for("login"))


@app.route('/login')
def login():
    """
    Display the login form.
    :return: Login webpage
    """
    return render_template('frontend/login.html')


@app.route('/save', methods=['POST'])
def save():
    """
    Save a valence value and respective video timestamp to the database.
    :return: Feedback string
    """
    if not session.get('username'):
        return "Error: username not set"
    else:
        d.insert_post({"timestamp": request.form.get('timestamp'),
                       "value": request.form.get('value'),
                       "videoname": request.form.get('videoname'),
                       "username": session['username']})
        return "Saving completed"


@app.route('/submit_username', methods=['POST'])
def submit_username():
    """
    Save a username for the current session.
    :return: Redirect to /index
    """
    session['username'] = request.form.get('username')
    return redirect(url_for('index'))


@app.route('/researcher_view', methods=['GET'])
def chart():
    """
    Display the web page for the researcher view
    :return: Researcher view webpage
    """
    data2 = collect_mongodbobjects(d)
    jsonData2 = json.loads(data2)
    df = pd.DataFrame(jsonData2)
    data_valence = df.objects.apply(lambda x: pd.Series(x))

    TOOLS = 'save,pan,box_zoom,reset,wheel_zoom,hover'

    p = figure(title="Valence ratings by timestamp", y_axis_type="linear",
               x_range=(0, 23), y_range=(0, 100), plot_height=400,
               tools=TOOLS, plot_width=900)
    p.xaxis.axis_label = 'Timestamp (seconds)'
    p.yaxis.axis_label = 'Valence rating'

    x = data_valence.timestamp
    y = data_valence.value
    # spl = CubicSpline(x, y)
    # When adding above CubicSpline, following error is produced:

    # TypeError: ufunc 'isfinite' not supported for the input types, and the inputs could not be safely coerced to any supported types according to the casting rule ''safe''
    # so there might be some requirement in CubicSpline source code to
    # have all x values certain type

    # y_smooth = spl(data_valence.value)
    # y_smooth = spline(data_valence.timestamp, data_valence.value)
    p.line(x, y, line_color="purple", line_width=3)
    # p.line(data_valence.timestamp, y_smooth,line_color="purple", line_width = 3)

    source = ColumnDataSource(data={
        'timestamp': data_valence.timestamp,
        'value': data_valence.value,
        'videoname': data_valence.videoname})

    p.select_one(HoverTool).tooltips = [
        ('timestamp', '@x'),
        ('Rating of valence', '@y')
    ]

    script, div = components(p)
    return render_template("frontend/researcher_view.html", the_div=div,
                           the_script=script)


@app.route('/collect_data')
def collect_data():
    """
    Function to print all data that is stored in the MongoDB database.
    :return: Webpage displaying currently stored data
    """
    return collect_mongodbobjects(d)


@app.route('/delete_all')
def delete_data():
    """
    Delete all data that is stored in the MongoDB database.
    :return: User feedback string
    """
    d.delete_many({})
    return "All items deleted :)"


@app.route('/<path:path>')
def static_file(path):
    """
    Dunno what this does.
    :param path: ?
    :return: ?
    """
    return app.send_static_file(path)
