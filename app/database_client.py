"""
This file contains the interface object for the MongoDB database.
"""

from pymongo import MongoClient

class DatabaseClient:
    """
    Class specifying the connection to the MongoDB database.
    """

    def __init__(self):
        """
        Initiate connection to the database "videoannotatordb".
        """
        DB_NAME = "videoannotatordb"
        DB_HOST = "ds159185.mlab.com"
        DB_PORT = 59185
        DB_USER = "videoadmin"
        DB_PASS = "kantapassu123"

        client = MongoClient(DB_HOST, DB_PORT)
        db = client[DB_NAME]
        db.authenticate(DB_USER, DB_PASS)
        self.posts = db.posts

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