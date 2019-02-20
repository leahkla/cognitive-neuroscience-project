from pymongo import MongoClient

class DatabaseClient:

    def __init__(self):
        client = MongoClient()
        db = client.pymongo_test
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