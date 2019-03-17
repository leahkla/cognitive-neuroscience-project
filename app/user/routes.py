"""
This file contains the routes, i.e. the functions to be executed when a page
(like "/index") is accessed in the browser.

It has only the webpages belonging to the user blueprint,
i.e. those belonging to the user interface.
"""

from flask import render_template

from app.user import bp
from app.functionalities import check_access_right


@bp.route('/user')
def user():
    """
    Display the main user page.

    This is not accessible for somebody with the role researcher.
    :return: Main webpage
    """
    check_access_right(forbidden='researcher', redirect_url='researcher.chart')
    return render_template('user/user.html')
