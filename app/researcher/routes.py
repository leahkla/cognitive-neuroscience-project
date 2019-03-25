"""
This file contains the routes, i.e. the functions to be executed when a page
(like "/researcher_view") is accessed in the browser.

It has only the webpages belonging to the researcher blueprint,
i.e. those belonging to the researcher interface.
"""

import json
import pandas as pd
from flask import render_template, flash
import numpy as np

from bokeh.models import HoverTool
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.palettes import Spectral6

from app.researcher import bp
from app.functionalities import collect_mongodbobjects, check_access_right
from app import d

# PChipInterpolator finds monotonic interpolations, which we need to make
# sure that our interpolated values don't go below 0 or above 100.
from scipy.interpolate import PchipInterpolator


# from scipy.interpolate import spline
# from scipy.interpolate import interp1d

@bp.route('/chart', methods=['GET'])
def chart():
    """
    Display the web page for the researcher view.

    This webpage is only for the role researcher.
    :return: Researcher view webpage
    """
    check_access_right(forbidden='user', redirect_url='control.index')

    # Get the data:
    data = collect_mongodbobjects(d)
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_numeric(df['timestamp'])
    df['value'] = pd.to_numeric(df['value'])
    df.sort_values(by=['timestamp'], inplace=True)

    # Group by username and extract timestamps and values for each user
    grouped_data = df.groupby('username')
    data_by_user = [user for _, user in grouped_data]
    ts = [np.array(t) for t in
          (data_by_user[i]['timestamp'].apply(lambda x: float(x)) for i in
           range(len(data_by_user)))]
    vals = [np.array(val) for val in
            (data_by_user[i]['value'].apply(lambda x: float(x)) for i in
             range(len(data_by_user)))]

    # Make sure all data starts and ends at the same time for each user, if the
    # data doesn't suggest otherwise start and end value are 50.
    max_t = max([max(t) for t in ts])
    for i in range(len(ts)):
        if min(ts[i]) != 0:
            ts[i] = np.append([0], ts[i])
            vals[i] = np.append([50], vals[i])
        if max(ts[i]) != max_t:
            ts[i] = np.append(ts[i], [max_t])
            vals[i] = np.append(vals[i], [50])
        # Round last timestamp up (for smoother display):
        ts[i] = np.append(ts[i][:-1], int(ts[i][-1])+1)

    # Create the interpolation
    xs = np.arange(0, int(max_t) + 1.5, 1)
    interpolators = [PchipInterpolator(t, val) for (t, val) in zip(ts, vals)]
    user_timeseries = [[xs, interpolator(xs)] for interpolator in interpolators]

    # Create the Bokeh plot
    TOOLS = 'save,pan,box_zoom,reset,wheel_zoom,hover'
    p = figure(title="Valence ratings by timestamp", y_axis_type="linear",
               plot_height=500,
               tools=TOOLS, active_scroll='wheel_zoom', plot_width=900)
    p.xaxis.axis_label = 'Timestamp (seconds)'
    p.yaxis.axis_label = 'Valence rating'

    for i, tseries in enumerate(user_timeseries):
        p.line(tseries[0], tseries[1], line_color=Spectral6[i%6],
               line_width=3, name=data_by_user[i]['username'].iloc[0])
    for i in range(len(ts)):
        for j in range(len(ts[i])):
            p.circle(ts[i][j], vals[i][j], fill_color=Spectral6[i%6],
                     line_color='black', radius=0.7)

    p.select_one(HoverTool).tooltips = [
        ('Time', '@x'),
        ('Valence', '@y'),
        ('User', '$name')

    ]

    script, div = components(p)
    return render_template("researcher/researcher.html", the_div=div,
                           the_script=script)


@bp.route('/correlations', methods=['GET'])
def correlations():
    check_access_right(forbidden='user', redirect_url='control.index')

    return render_template("researcher/correlations.html")
