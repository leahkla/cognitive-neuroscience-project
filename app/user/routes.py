"""
This file contains the routes, i.e. the functions to be executed when a page
(like "/index") is accessed in the browser.

It has only the webpages belonging to the user blueprint,
i.e. those belonging to the user interface.
"""

from flask import render_template, request, flash

from app.user import bp
from app.functionalities import check_access_right


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

    vid_file = 'app/user/video_conf.txt'
    with open(vid_file) as f:
        videos = f.readlines()
    vid_list = [x.strip() for x in videos if x.strip() if
                (x.strip()[0] is not '#')]
    vid_dict = dict([map(str.strip, i.split(':')) for i in vid_list])

    cur_vid_id = request.args.get('vid')
    if not cur_vid_id:
        currentVideo = vid_list[0].split(':')
    else:
        currentVideo = [cur_vid_id, vid_dict[cur_vid_id]]

    return render_template('user/user.html', vid_dict=vid_dict,
                           currentVideo=currentVideo)
