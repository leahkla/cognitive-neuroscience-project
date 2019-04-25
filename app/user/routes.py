"""
This file contains the routes, i.e. the functions to be executed when a page
(like "/index") is accessed in the browser.

It has only the webpages belonging to the user blueprint,
i.e. those belonging to the user interface.
"""

from flask import render_template, flash, current_app, request

from app.user import bp
from app.functionalities import check_access_right, get_video_information, \
    get_input_fields


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

    check_access_right(forbidden='researcher', redirect_url='control.index')

    currentVideo, vid_dict, _ = get_video_information(
        cur_vid_id=request.args.get('vid'))

    field_list = get_input_fields()

    oneDsliders = [x for x in field_list if x[0]=='slider']
    twoDsliders = [x for x in field_list if x[0]=='2dslider']

    if len(oneDsliders) > 2:
        oneDsliders = oneDsliders[:2]
        flash('Currently, at most two one-dimensional sliders are supported.')
    if len(twoDsliders) > 1:
        twoDsliders = twoDsliders[:1]
        flash('Currently, only one (or zero) two-dimensional sliders are '
              'supported.')

    return render_template('user/user.html', vid_dict=vid_dict,
                           currentVideo=currentVideo, oneDsliders=oneDsliders,
                           twoDsliders=twoDsliders)


@bp.route('/userinstructions')
def userinstructions():
    """
    Display the instruction page for the user, which looks different
    depending on whether the person accessing has the role user or researcher
    :return: User instructions webpage.
    """
    check_access_right(forbidden='', redirect_url='control.index')

    with open(current_app.user_instructions_file, 'r') as f:
        instructions = f.read()

    return render_template('user/userinstructions.html',
                           instructions=instructions)
