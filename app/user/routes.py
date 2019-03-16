"""
This file contains the routes, i.e. the functions to be executed when a page
(like "/index") is accessed in the browser.

It has only the webpages belonging to the user blueprint,
i.e. those belonging to the user interface.
"""

from flask import redirect, url_for, render_template, session

from app.user import bp

@bp.route('/index')
@bp.route('/')
def index():
    """
    Display the main user page.
    :return: Main webpage
    """
    if session.get('username'):
        return render_template('frontend/index.html') # "base.html"
    else:
        return redirect(url_for("control.login"))