"""
This file contains the interface class for the MongoDB database.
"""
from flask import current_app

from pymongo import MongoClient

class DatabaseClient:
    """
    Class specifying the connection to the MongoDB database.
    """

    def __init__(self):
        """
        Initiate the database connection.
        Depending on the DB_TYPE environment variable it will be connected to a
        local database (this requires to have MongoDB running on the local
        machine), or to the dev-database or to a production database
        (which is the default).
        """
        type = current_app.config['DB_TYPE']
        if type == 'local':
            client = MongoClient()
            db = client.videoannotatordb
        else:
            if type == 'dev':
                DB_NAME = "videoannotatordbdev"
                DB_HOST = "ds231956.mlab.com"
                DB_PORT = 31956
                DB_USER = "videoadmin"
                DB_PASS = "kantapassu123"
            else: # type ='prod'
                DB_NAME = "videoannotatordb"
                DB_HOST = "ds159185.mlab.com"
                DB_PORT = 59185
                DB_USER = "videoadmin"
                DB_PASS = "kantapassu123"
            client = MongoClient(DB_HOST, DB_PORT)
            db = client[DB_NAME]
            db.authenticate(DB_USER, DB_PASS)
        self.posts = db.posts
        self.type=type

    def insert_post_with_removal(self, post_data):
        """
        Not sure what exactly this is doing.
        :param post_data: Data is to be posted
        :return: None
        """
        self.posts.delete_many({})
        self.posts.insert_one(post_data)

    def insert_post(self, post_data):
        """
        Insert a post into the database.
        :param post_data: Data is to be posted
        :return: None
        """
        self.posts.insert_one(post_data)

    def collect_posts(self):
        """
        Collect all entries from the database.
        :return: Contents of the database
        """
        return self.posts.find()

    def delete_many(self, rule):
        """
        Delete posts according to a rule.
        :param rule: The rule
        :return: None
        """
        self.posts.delete_many(rule)