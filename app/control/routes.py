"""
This file contains the routes, i.e. the functions to be executed when a page
(like "/login") is accessed in the browser.

It has only the webpages belonging to control functions of our app,
i.e. those belonging to the control blueprint.
"""

from flask import request, redirect, url_for, render_template, session, flash

from app.functionalities import collect_mongodbobjects, check_access
from app.control import bp
from app import d


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
        return render_template('user/user.html')
    if session.get('role') == 'researcher':
        # Role is 'researcher'
        return render_template('researcher.chart')
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
    if (not username) and (role != "researcher"):
        # Role is not researcher, but username is not provided
        flash('Please provide a username.')
        return redirect(url_for('control.login'))
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

    Operation is not allowed for role user.
    :return: Webpage displaying currently stored data
    """
    check_access(forbidden='user', redirect_url='control.index',
                 msg='Not allowed!')
    return collect_mongodbobjects(d)


@bp.route('/delete_all')
def delete_data():
    """
    Delete all data that is stored in the MongoDB database.

    Operation is not allowed for role user.
    :return: User feedback string
    """
    check_access(forbidden='user', redirect_url='control.index',
                 msg='Not allowed!')
    d.delete_many({})
    return redirect(url_for('control.collect_data'))
