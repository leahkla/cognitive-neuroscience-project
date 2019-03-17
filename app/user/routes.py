"""
This file contains the routes, i.e. the functions to be executed when a page
(like "/index") is accessed in the browser.

It has only the webpages belonging to the user blueprint,
i.e. those belonging to the user interface.
"""

from flask import render_template

from app.user import bp


@bp.route('/user')
def user():
    """
    Display the main user page.
    :return: Main webpage
    """
    return render_template('user/user.html')
