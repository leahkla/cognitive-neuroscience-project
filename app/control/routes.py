"""
This file contains the routes, i.e. the functions to be executed when a page
(like "/login") is accessed in the browser.

It has only the webpages belonging to control functions or our app,
i.e. those belonging to the control blueprint.
"""

from flask import request, redirect, url_for, render_template, session

from app.helper_functions import collect_mongodbobjects
from app.control import bp
from app import d


@bp.route('/login')
def login():
    """
    Display the login form.
    :return: Login webpage
    """
    return render_template('frontend/login.html')


@bp.route('/submit_username', methods=['POST'])
def submit_username():
    """
    Save a username for the current session.
    :return: Redirect to /index
    """
    session['username'] = request.form.get('username')
    return redirect(url_for('user.index'))


@bp.route('/save', methods=['POST'])
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


@bp.route('/<path:path>')
def static_file(path):
    """
    Dunno what this does.
    :param path: ?
    :return: ?
    """
    return bp.send_static_file(path)


@bp.route('/collect_data')
def collect_data():
    """
    Function to print all data that is stored in the MongoDB database.
    :return: Webpage displaying currently stored data
    """
    return collect_mongodbobjects(d)


@bp.route('/delete_all')
def delete_data():
    """
    Delete all data that is stored in the MongoDB database.
    :return: User feedback string
    """
    d.delete_many({})
    return "All items deleted :)"
