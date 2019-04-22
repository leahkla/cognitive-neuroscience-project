"""
This file contains the routes, i.e. the functions to be executed when a page
(like "/chart") is accessed in the browser.

It has only the webpages belonging to the researcher blueprint,
i.e. those belonging to the researcher interface.
"""

import json
import pandas as pd
from flask import render_template, flash, current_app, request
import numpy as np

from bokeh.models import HoverTool
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.palettes import Spectral6
from bokeh.layouts import row
from bokeh.models.annotations import Title

from app.researcher import bp
from app.functionalities import collect_mongodbobjects, check_access_right, \
    get_interpolators, get_videos

# PChipInterpolator finds monotonic interpolations, which we need to make
# sure that our interpolated values don't go below 0 or above 100.
from scipy.interpolate import PchipInterpolator

from tslearn.clustering import TimeSeriesKMeans
from tslearn.datasets import CachedDatasets
from tslearn.preprocessing import TimeSeriesScalerMeanVariance, \
    TimeSeriesResampler

"""from rpy2.robjects import DataFrame, FloatVector, IntVector, r
from rpy2.robjects.packages import importr
from math import isclose
"""

@bp.route('/chart', methods=['GET'])
def chart():
    """
    Display the web page for the researcher view.

    This webpage is only for the role researcher.
    :return: Researcher view webpage
    """
    check_access_right(forbidden='user', redirect_url='control.index')

    # Get the data:
    _, data = collect_mongodbobjects()
    data['timestamp'] = pd.to_numeric(data['timestamp'])
    data['value'] = pd.to_numeric(data['value'])
    data.sort_values(by=['timestamp'], inplace=True)

    # Group by username and extract timestamps and values for each user
    grouped_data = data.groupby('username')
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
        ts[i] = np.append(ts[i][:-1], int(ts[i][-1]) + 1)

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
        p.line(tseries[0], tseries[1], line_color=Spectral6[i % 6],
               line_width=3, name=data_by_user[i]['username'].iloc[0])
    for i in range(len(ts)):
        for j in range(len(ts[i])):
            p.circle(ts[i][j], vals[i][j], fill_color=Spectral6[i % 6],
                     line_color='black', radius=0.7)

    p.select_one(HoverTool).tooltips = [
        ('Time', '@x'),
        ('Valence', '@y'),
        ('User', '$name')

    ]

    script, div = components(p)
    return render_template("researcher/chart.html", the_div=div,
                           the_script=script)


def eucl(a, b):
    return np.sqrt((a-b)**2)

@bp.route('/correlations', methods=['GET'])
def correlations():
    """
        Display correlation plot for the researcher.

        This webpage is only for the role researcher.
        :return: Correlation plot
        """
    check_access_right(forbidden='user', redirect_url='control.index')
    vid_dict, first_vid = get_videos()
    print(vid_dict)
    cur_vid_id = request.args.get('vid')
    if not cur_vid_id:
        currentVideo = first_vid
    else:
        currentVideo = [cur_vid_id, vid_dict[cur_vid_id]]
    _, data = collect_mongodbobjects(cur_vid_id)

    # Get interpolators from functionalities.py
    interpolators, max_t = get_interpolators(data)
    xs = np.arange(0, int(max_t) + 1.5, 1)

    # Generate data
    user_timeseries = [[interpolator(xs)] for interpolator in interpolators]

    seed = np.random.randint(0,100000,1)[0]
    np.random.seed(seed)

    # Set cluster count
    n_clusters = 3
    if n_clusters > np.array(user_timeseries).shape[0]:
        n_clusters = np.array(user_timeseries).shape[0]

    # Euclidean k-means
    km = TimeSeriesKMeans(n_clusters=n_clusters, verbose=True,
                          random_state=seed)
    y_pred = km.fit_predict(user_timeseries)

    # Generate plots and calculate statistics
    all_plots = ""
    all_scripts = ""
    plots = [] 

    ### TODO MAYBE: intra-cluster correlation with rpy2. Might not work with matrices
    """    valmatrix = np.empty([24,151])
    for iii in range(24):
        valmatrix[iii, :] = user_timeseries[iii][0]
    print(type(valmatrix), valmatrix.shape)
    print(type(valmatrix[0]), len(valmatrix[0]))
    print(type(valmatrix[0][0]))
    r_icc = importr("ICC", lib_loc="C:/Users/Lauri Lode/Documents/R/win-library/3.4")
    #m = r.matrix(FloatVector(valmatrix.flatten()), nrow=24)
    df = DataFrame({"groups": IntVector(y_pred),
        "values": FloatVector(valmatrix.flatten())})
    
    icc_res = r_icc.ICCbare("groups", "values", data=df)
    icc_val = icc_res[0]
    print("ICC" + str(icc_val))"""

    for yi in range(n_clusters):
        p = figure(plot_width=350, plot_height=300)
        n=0
        values = km.cluster_centers_[yi].ravel()
        centerMean = np.mean(km.cluster_centers_[yi].ravel())
        varsum = 0
        for xx in range(0, len(y_pred)):
            if y_pred[xx] == yi:
                n = n+1
                for iii in range(len(user_timeseries[xx][0])):
                    varsum = varsum + eucl(user_timeseries[xx][0][iii], values[iii])/len(user_timeseries[xx][0])

                p.line(range(0, len(user_timeseries[xx][0])),
                       user_timeseries[xx][0], line_width=0.3)
        varsum = np.sqrt(varsum)

        titleString = "C#" + str(yi + 1) + ", n: " + str(n) +", μ: " + str(np.round(centerMean, decimals=3)) + ", σ: " + str(np.round(varsum, decimals=3)) + ", σ²: " + str(np.round(varsum**2, decimals=3))
        t = Title()
        t.text = titleString
        p.title = t
        p.line(range(0, len(values)), values, line_width=2)
        plots.append(p)

    # Get plot codes
    script, div = components(row(plots))
    print(vid_dict)

    return render_template("researcher/correlations.html", the_div=div,
                           the_script=script, vid_dict=vid_dict, currentVideo=currentVideo)


@bp.route('/config')
def config():
    """
    Display the configuarion page, where the user can add or remove videos or
    change the database this is connected to.
    :return: Renders the website
    """
    check_access_right(forbidden='user', redirect_url='control.index')

    vid_dict, _ = get_videos()

    return render_template("researcher/config.html", vid_dict=vid_dict,
                           dbs=current_app.dbs,
                           cur_db=current_app.config['DB'])
