"""
This file contains the routes, i.e. the functions to be executed when a page
(like "/choose_role") is accessed in the browser.

It has only the webpages belonging to control functions of our app,
i.e. those belonging to the control blueprint.
"""
from flask import request, redirect, url_for, render_template, session, \
    flash, send_file, current_app

import pandas as pd
from io import StringIO, BytesIO
import datetime

from app.functionalities import collect_mongodbobjects, check_access_right, \
    sort_df, signal_data_modification
from app.control import bp
from app.database_client import DatabaseClient
import pymongo
from werkzeug.contrib.cache import SimpleCache


@bp.route('/')
def index():
    """
    Ask user to provide user name or redirect him to the user page if user
    name is already available.
    :return: Main webpage
    """
    if ((session.get('role') == 'user') or (
            session.get('role') == 'test')) and session.get('username'):
        # Role is 'user' or 'test' and username is provided
        return redirect(url_for('user.user'))
    if session.get('role') == 'researcher':
        # Role is 'researcher'
        return redirect(url_for('researcher.chart'))
    else:
        return redirect(url_for("control.choose_role"))


@bp.route('/choose_role')
def choose_role():
    """
    Display the choose_role form.
    :return: Role choosing webpage
    """
    return render_template('control/choose_role.html')


@bp.route('/submit_username', methods=['POST'])
def submit_username():
    """
    Save a username for the current session.
    :return: Redirect to /index
    """
    username = request.form.get('username')
    role = request.form.get('role')
    if (not username) and (role != "researcher"):
        # Role is not researcher, but username is not provided
        flash('Please provide a username.')
        return redirect(url_for('control.choose_role'))
    session['role'] = role
    if role == 'researcher':
        # If role is researcher, username does not need to be stored
        return redirect(url_for('researcher.chart'))
    session['username'] = username
    return redirect(url_for('user.user'))


@bp.route('/save', methods=['POST'])
def save():
    """
    Save a valence value and respective video timestamp to the database.
    :return: Feedback string
    """
    if not session.get('username'):
        return "Error: username not set"
    else:
        current_app.d.insert_post({"videoid": request.form.get('videoid'),
                                   "username": session['username'],
                                   "timestamp": request.form.get('timestamp'),
                                   "value": request.form.get('value'),
                                   "date": request.form.get('date')
                                   })
        signal_data_modification(request.form.get('videoid'))
        return "Saving completed"


@bp.route('/save2D', methods=['POST'])
def save2D():
    """
    Save a valence value and respective video timestamp to the database.
    :return: Feedback string
    """
    if not session.get('username'):
        return "Error: username not set"
    else:
        current_app.d.insert_post({"videoid": request.form.get('videoid'),
                                   "username": session['username'],
                                   "timestamp": request.form.get('timestamp'),
                                   "value": request.form.get('value'),
                                   "value2": request.form.get('value2'),
                                   "date": request.form.get('date')
                                   })
        signal_data_modification(request.form.get('videoid'))
        return "Saving completed"


@bp.route('/<path:path>')
def static_file(path):
    """
    Dunno what this does.
    :param path: ?
    :return: ?
    """
    return bp.send_static_file(path)


@bp.route('/data')
def data():
    """
    Function to print all data that is stored in the MongoDB database.

    Operation is not allowed for role user.
    :return: Webpage displaying currently stored data
    """
    check_access_right(forbidden='user', redirect_url='control.index')
    b, data = collect_mongodbobjects()
    if b:
        # The names of the data fields:
        headers = list(data)
        # And a list of their contents:
        data_rows = list(data.values)
        return render_template('control/data.html', data=data_rows,
                               headers=headers)
    else:
        return render_template('control/data.html', data='', headers='')


@bp.route('/export_all')
def export_all():
    """
    Export all the data stored in MongoDB to a file

    Operation is not allowed for role user.
    :return:
    """
    check_access_right(forbidden='user', redirect_url='control.index')
    b, data = collect_mongodbobjects()
    if b:
        bytes_buffer = BytesIO()
        with StringIO() as str_buffer:
            data.to_csv(str_buffer, index=False)
            str_buffer.seek(0)
            bytes_buffer.write(str_buffer.getvalue().encode('utf-8'))
        bytes_buffer.seek(0)
        filename = 'video_annotations_{date:%Y-%m-%d_%H-%M-%S}.csv'.format(
            date=datetime.datetime.now())
        return send_file(bytes_buffer,
                         as_attachment=True, attachment_filename=filename,
                         mimetype='text/csv')
    else:
        flash('No data to export!')
        return render_template('control/data.html', data='', headers='')


@bp.route('/delete_all')
def delete_all():
    """
    Delete all data that is stored in the MongoDB database.

    Operation is not allowed for role user.
    :return: User feedback string
    """
    check_access_right(forbidden='user', redirect_url='control.index')
    current_app.d.delete_many({})
    current_app.config['CACHE'] = SimpleCache(default_timeout=1000000000000000000000)
    flash('All data deleted!')
    return redirect(url_for('control.data'))


@bp.route('/add_video', methods=['POST'])
def add_video():
    """
    Add a new video to the file video_conf.txt
    :return: Redirects to researcher.config
    """
    vid_id = request.form.get('vid_id')
    vid_name = request.form.get('vid_name')

    if (not vid_id) or (not vid_name):
        flash("You need to provide a video ID (or its URL) and video name in "
              "order to add a video")
    else:
        if not vid_id.isdigit():
            # If the whole video url is given
            vid_id = vid_id.split('/')[-1]
            if not vid_id.isdigit():
                flash(
                    'Error, the URL seems to be not of the write format. It '
                    'should end in a number, like for example '
                    '"https://vimeo.com/65107797"')
                return (redirect(url_for('researcher.config')))
        with open(current_app.vid_file, 'a') as f:
            f.write('\n' + vid_id + ':' + vid_name)
        flash('Video "' + vid_name + '" was successfully added.')

    return redirect(url_for('researcher.config'))


@bp.route('/remove_video')
def remove_video():
    """
    Remove a video from the file video_conf.txt
    :return: Redirects to researcher.config
    """
    vid_id = request.args.get('vid_id')
    vid_name = request.args.get('vid_name')

    removed = False

    with open(current_app.vid_file, 'r') as f:
        lines = f.readlines()
    with open(current_app.vid_file, 'w') as f:
        for line in lines:
            if vid_id not in line:
                f.write(line)
            else:
                removed = True

    if removed:
        flash('Video "' + vid_name + '" has been removed.')
    else:
        flash('Video "' + vid_name + '" not found. Nothing removed.')

    return redirect(url_for('researcher.config'))


@bp.route('/change_db', methods=['POST'])
def change_db():
    """

    :return:
    """
    new_db = request.form.get('db')
    current_app.config['DB'] = new_db

    current_app.d = DatabaseClient()

    flash('Database changed to "' + current_app.dbs[new_db] + '".')
    return redirect(url_for('researcher.config'))
