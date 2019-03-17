"""
This file contains the routes, i.e. the functions to be executed when a page
(like "/login") is accessed in the browser.

It has only the webpages belonging to control functions of our app,
i.e. those belonging to the control blueprint.
"""

from flask import request, redirect, url_for, render_template, session, flash

from app.functionalities import collect_mongodbobjects
from app.control import bp
from app import d


@bp.route('/')
def index():
    """
    Ask user to provide user name or redirect him to the user page if user
    name is already available.
    :return: Main webpage
    """
    if session.get('username'):
        return render_template('user/user.html')
    else:
        return redirect(url_for("control.login"))


@bp.route('/login')
def login():
    """
    Display the login form.
    :return: Login webpage
    """
    return render_template('control/login.html')


@bp.route('/submit_username', methods=['POST'])
def submit_username():
    """
    Save a username for the current session.
    :return: Redirect to /index
    """
    username = request.form.get('username')
    role = request.form.get('role')
    # Check if username was provided:
    if (not username) and (role != "researcher"):
        flash('Please provide a username.')
        return redirect(url_for('control.login'))
    session['role'] = role
    # If the role is researcher don't even store the username, just redirect to
    # the researcher url:
    if role == 'researcher':
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
