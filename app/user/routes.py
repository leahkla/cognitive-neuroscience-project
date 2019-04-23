"""
This file contains the routes, i.e. the functions to be executed when a page
(like "/index") is accessed in the browser.

It has only the webpages belonging to the user blueprint,
i.e. those belonging to the user interface.
"""

from flask import render_template, request, flash

from app.user import bp
from app.functionalities import check_access_right, get_videos, get_video_information


@bp.route('/user')
def user():
    """
    Display the main user page.
    [The videos that can be accessed have to be defined with name and vimeo
    ID in a dictionary here.]

    This is not accessible for somebody with the role researcher.
    :return: Main webpage
    """
    # videos = {'Omelette':'65107797', 'Happiness':'28374299'}

    check_access_right(forbidden='researcher', redirect_url='researcher.chart')

    currentVideo, cur_vid_id, vid_dict = get_video_information(request)

    return render_template('user/user.html', vid_dict=vid_dict,
                           currentVideo=currentVideo)


@bp.route('/userinstructions')
def userinstructions():
    """
    Display the instruction page for the user.
    
    """
    return render_template('user/userinstructions.html')

    
