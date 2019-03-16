""""
This file contains functions that are needed in the routes.py files to
display the webpages, but do not have a decorator binding them to a
particular webpage.
"""

import json


######### Database ##########

def collect_mongodbobjects(db_client):
    """
    Fetch all data that is stored in the MongoDB database.
    :param db_client: The databas client
    :return: json of all the db entries
    """
    posts = db_client.collect_posts()
    collected = []
    for p in posts:
        if p['_id']:
            del p['_id']
        collected.append(p)
    return json.dumps({"objects": collected})

####### Visualisation #######

# no functions in here as of yet
