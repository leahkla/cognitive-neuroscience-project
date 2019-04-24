""""
This file contains functions that are needed in several routes.py files to
display the webpages, but do not have a decorator binding them to a
particular webpage.
"""
from flask import session, url_for, flash, current_app
from werkzeug.routing import RequestRedirect
import pandas as pd
import numpy as np
from scipy.interpolate import PchipInterpolator
import pymongo
from bokeh.models import HoverTool
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.palettes import Spectral6


def eucl(a, b):
    return np.sqrt((a - b) ** 2)


def collect_mongodbobjects(videoid=None):
    """
    Fetch all data that is stored in the MongoDB database.

    NB: This already processes them as a DataFrame using sort_df(),
    which means that the names and variable types of the data must be known
    in advance (they're hardcoded, see sort_df() ).
    :return: Boolean indicating availability of data, DataFrame with all db
    entries
    """
    posts = current_app.d.collect_posts()
    collected = []
    for p in posts:
        if p['_id']:
            del p['_id']
        if videoid == None or p['videoid'] == videoid:
            collected.append(p)

    # If there is data at all
    if collected:
        df = pd.DataFrame(collected)
        df = sort_df(df)
        return True, df
    else:
        return False, None


def sort_df(df):
    """
    Reorder columns in a dataframe, give them suitable data types and sort the
    values.

    :param df: Dataframe to be sorted
    :return: Sorted dataframe
    """
    try:
        ordered_cols = ['videoid', 'username', 'timestamp', 'value', 'value2',
                        'date']
        col_types = ['str', 'str', 'float', 'int', 'int', 'str']
        df = df[ordered_cols]
        for t, c in zip(col_types, ordered_cols):
            df[c] = df[c].astype(t)
        df.sort_values(ordered_cols, inplace=True)
    except:
        print("Error! Values are not in right types")
        print(df)
    return df


def check_access_right(forbidden, redirect_url, msg='default'):
    """
    Check if access to a given page is allowed with the current role (the one
    saved in session['role']).
    N.B. Use werkzeug for redirect, the flask redirect function does not work here.
    :param forbidden: The role that is forbidden
    :param redirect_url: The URL to redirect to, e.g. 'control.choose_role'
    :param msg: Message, if there is a message to be flushed. Defaults to
    'default'.
    :return: Redicrects to other page if access not allowed
    """
    if 'role' not in session.keys():
        # If the user has no role yet redirect to choose one.
        raise RequestRedirect(url_for('control.choose_role'))
    if session['role'] != forbidden:
        # Access approved!
        return None
    else:
        # Access denied, redirect.
        if msg:
            if msg == 'default':
                msg = "You can't access that page with your role (current " \
                      "role: " + str(session['role']) + ")."
            flash(msg)
        raise RequestRedirect(url_for(redirect_url))


def get_interpolators(df):
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
        ts[i] = np.append(ts[i][:-1], int(ts[i][-1]) + 1)

    # Create the interpolation
    interpolators = [PchipInterpolator(t, val) for (t, val) in zip(ts, vals)]
    return interpolators, max_t


def get_videos():
    """
    Find the currently available video names and ids.
    :return: Dictionary of available videos, each stored as id:name, and list
    containing id and name of the video that is the first one in the file.
    """
    with open(current_app.vid_file, 'r') as f:
        videos = f.readlines()
    vid_list = [x.strip() for x in videos if x.strip() if
                (x.strip()[0] is not '#')]
    vid_dict = dict([i.split(':', 1) for i in vid_list])
    first_vid = vid_list[0].split(':', 1)
    return vid_dict, first_vid


def get_video_information(request):
    """
        Parse video information for nice form based on get_video() result and a request query parameter
        :return: Current video, id of the current video and dictionary of available videos (described more detailly in get_videos() )
        """
    vid_dict, first_vid = get_videos()
    cur_vid_id = request.args.get('vid')
    currentCluster = request.args.get('cluster')
    if not cur_vid_id:
        currentVideo = first_vid
    else:
        currentVideo = [cur_vid_id, vid_dict[cur_vid_id]]

    if not currentCluster:
        n_clusters = 3
    else:
        n_clusters = int(currentCluster)
    return currentVideo, cur_vid_id, vid_dict, n_clusters


def signal_data_modification(video_id):
    """
            Signal cache that data of specified video id has changed. This causes re-calculating plots later.
            """
    current_app.config['CACHE'].set(video_id + 'modified_correlations', True)
    current_app.config['CACHE'].set(video_id + 'modified_chart', True)


def calculate_chart(currentVideo):
    """
            Calculate bokeh chart of specific video and save it to cache 
            """
    _, data = collect_mongodbobjects(currentVideo)

    current_video_status = current_app.config['CACHE'].get(
        currentVideo + 'modified_chart')
    if current_video_status == True or current_video_status == None:
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
        interpolators = [PchipInterpolator(t, val) for (t, val) in
                         zip(ts, vals)]
        user_timeseries = [[xs, interpolator(xs)] for interpolator in
                           interpolators]

        # Create the Bokeh plot
        TOOLS = 'save,pan,box_zoom,reset,wheel_zoom,hover'
        p = figure(title="Valence ratings by timestamp", y_axis_type="linear",
                   plot_height=500,
                   tools=TOOLS, active_scroll='wheel_zoom', plot_width=900)
        p.xaxis.axis_label = 'Timestamp (seconds)'
        p.yaxis.axis_label = 'Valence rating'

        for i, tseries in enumerate(user_timeseries):
            p.line(tseries[0], tseries[1], line_color=Spectral6[i % 6],
                   line_width=1.5, name=data_by_user[i]['username'].iloc[0])
        for i in range(len(ts)):
            for j in range(len(ts[i])):
                p.circle(ts[i][j], vals[i][j], fill_color=Spectral6[i % 6],
                         line_color='black', radius=0.5)

        p.select_one(HoverTool).tooltips = [
            ('Time', '@x'),
            ('Valence', '@y'),
            ('User', '$name')

        ]

        script, div = components(p)
        current_app.config['CACHE'].set(currentVideo + 'div_chart', div)
        current_app.config['CACHE'].set(currentVideo + 'script_chart', script)
        current_app.config['CACHE'].set(currentVideo + 'modified_chart', False)
