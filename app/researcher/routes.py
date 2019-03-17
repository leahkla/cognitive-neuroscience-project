"""
This file contains the routes, i.e. the functions to be executed when a page
(like "/researcher_view") is accessed in the browser.

It has only the webpages belonging to the researcher blueprint,
i.e. those belonging to the researcher interface.
"""

import json
import pandas as pd
from flask import render_template

from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure
from bokeh.embed import components

from app.researcher import bp
from app.functionalities import collect_mongodbobjects
from app import d


# from scipy.interpolate import CubicSpline
# from scipy.interpolate import spline
# from scipy.interpolate import interp1d

@bp.route('/chart', methods=['GET'])
def chart():
    """
    Display the web page for the researcher view
    :return: Researcher view webpage
    """
    data2 = collect_mongodbobjects(d)
    jsonData2 = json.loads(data2)
    df = pd.DataFrame(jsonData2)
    data_valence = df.objects.apply(lambda x: pd.Series(x))

    TOOLS = 'save,pan,box_zoom,reset,wheel_zoom,hover'

    p = figure(title="Valence ratings by timestamp", y_axis_type="linear",
               x_range=(0, 23), y_range=(0, 100), plot_height=400,
               tools=TOOLS, plot_width=900)
    p.xaxis.axis_label = 'Timestamp (seconds)'
    p.yaxis.axis_label = 'Valence rating'

    x = data_valence.timestamp
    y = data_valence.value
    # spl = CubicSpline(x, y)
    # When adding above CubicSpline, following error is produced:

    # TypeError: ufunc 'isfinite' not supported for the input types, and the inputs could not be safely coerced to any supported types according to the casting rule ''safe''
    # so there might be some requirement in CubicSpline source code to
    # have all x values certain type

    # y_smooth = spl(data_valence.value)
    # y_smooth = spline(data_valence.timestamp, data_valence.value)
    p.line(x, y, line_color="purple", line_width=3)
    # p.line(data_valence.timestamp, y_smooth,line_color="purple", line_width = 3)

    source = ColumnDataSource(data={
        'timestamp': data_valence.timestamp,
        'value': data_valence.value,
        'videoname': data_valence.videoname})

    p.select_one(HoverTool).tooltips = [
        ('timestamp', '@x'),
        ('Rating of valence', '@y')
    ]

    script, div = components(p)
    return render_template("researcher/researcher.html", the_div=div,
                           the_script=script)
