from pymongo import MongoClient

class DatabaseClient:

    def __init__(self):
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
        self.posts.delete_many({})
        self.posts.insert_one(post_data)

    def insert_post(self, post_data):
        self.posts.insert_one(post_data)

    def collect_posts(self):
        return self.posts.find()

    def delete_many(self, rule):
        self.posts.delete_many(rule)