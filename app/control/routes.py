"""
This file contains the routes, i.e. the functions to be executed when a page
(like "/choose_role") is accessed in the browser.

It has only the webpages belonging to control functions of our app,
i.e. those belonging to the control blueprint.
"""
from flask import request, redirect, url_for, render_template, session, \
    flash, send_file, current_app

import json
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
        return redirect(url_for(current_app.user_default))
    if session.get('role') == 'researcher':
        # Role is 'researcher'
        return redirect(url_for(current_app.researcher_default))
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
    If the username provided is 'testing', the app will be put in test
    environment, which means the user has access to all webpages.
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
        return redirect(url_for('control.index'))
    if username == 'testing':
        # Set role to test
        session['role'] = 'test'
    session['username'] = username
    return redirect(url_for('control.index'))


@bp.route('/save', methods=['POST'])
def save():
    """
    Save a valence value and respective video timestamp to the database.
    :return: Feedback string
    """
    if not session.get('username'):
        return "Error: username not set"
    else:
        data_point = {"videoid": request.form.get('videoid'),
                      "username": session['username'],
                      "timestamp": request.form.get('timestamp'),
                      "date": request.form.get('date')
                      }
        values = json.loads(request.form.get('values'))
        names = json.loads(request.form.get('names'))
        for n, v in zip(names, values):
            data_point[n] = v

        current_app.d.insert_post(data_point)
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
    current_app.config['CACHE'] = SimpleCache(default_timeout=1e15)
    flash('All data deleted!')
    return redirect(url_for('researcher.data'))


@bp.route('/add_video', methods=['POST'])
def add_video():
    """
    Add a new video to the list of available videos.
    :return: Redirects to researcher.config.
    """
    check_access_right(forbidden='user', redirect_url='control.index')

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
    Remove a video from the available videos.
    :return: Redirects to researcher.config
    """
    check_access_right(forbidden='user', redirect_url='control.index')

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


@bp.route('/add_slider', methods=['POST'])
def add_slider():
    """
    Add a slider to the user page.
    :return: Redirects to researcher.config.
    """
    check_access_right(forbidden='user', redirect_url='control.index')

    slider_type = request.form.get('slider_type')

    min_val = request.form.get('min')
    max_val = request.form.get('max')
    def_val = request.form.get('def')
    name = request.form.get('name')
    if (not min_val) or (not max_val) or (not def_val) or (not name):
        flash("You need to provide values to all fields in order to add a "
              "slider!")
        return redirect(url_for('researcher.config'))

    if slider_type == 'slider':
        with open(current_app.input_fields, 'a') as f:
            f.write('\n' + slider_type + ':' + min_val + ':' + max_val + ':' +
                    def_val + ':' + name)
        flash('Slider "' + name + '" was successfully added.')

    elif slider_type == '2dslider':
        min_val2 = request.form.get('min2')
        max_val2 = request.form.get('max2')
        def_val2 = request.form.get('def2')
        name2 = request.form.get('name2')
        if (not min_val2) or (not max_val2) or (not def_val2) or (not name2):
            flash("You need to provide values to all fields in order to add a "
                  "slider!")
            return redirect(url_for('researcher.config'))
        with open(current_app.input_fields, 'a') as f:
            f.write(
                '\n' + slider_type + ':' + min_val + ':' + min_val2 + ':' + max_val + ':' + max_val2 + ':' +
                def_val + ':' + def_val2 + ':' + name + ':' + name2)
        flash('Slider "' + name + ':' + name2 + '" was successfully added.')

    else:
        flash(
            'Error, slider could not be added. Try reloading the page and trying again.')

    return (redirect(url_for('researcher.config')))


@bp.route('/remove_slider')
def remove_slider():
    """
    Remove a slider from the user page.
    :return: Redirects to researcher.config
    """
    check_access_right(forbidden='user', redirect_url='control.index')

    slider_name = request.args.get('slider_name')

    removed = False

    with open(current_app.input_fields, 'r') as f:
        lines = f.readlines()
    with open(current_app.input_fields, 'w') as f:
        for line in lines:
            if (line[-len(slider_name):] != slider_name) and (
                    line[-len(slider_name) - 1:] != slider_name + '\n'):
                f.write(line)
            else:
                removed = True

    if removed:
        flash('Slider "' + slider_name + '" has been removed.')
    else:
        flash('Slider "' + slider_name + '" does not exist. Nothing removed.')

    return redirect(url_for('researcher.config'))


@bp.route('/change_db', methods=['POST'])
def change_db():
    """
    Change the internal database in config['DB'] according to the database
    provided by the form.
    :return: Redirects to the configuration page for the researcher.
    """
    check_access_right(forbidden='user', redirect_url='control.index')

    new_db = request.form.get('db')
    current_app.config['DB'] = new_db

    current_app.d = DatabaseClient()

    flash('Database changed to "' + current_app.dbs[new_db] + '".')
    current_app.config['CACHE'] = SimpleCache(default_timeout=1e15)
    return redirect(url_for('researcher.config'))
