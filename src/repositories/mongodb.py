from pymongo import MongoClient
from typing import Any


class MongoConnection:
    def __init__(self, config: dict) -> None:
        self.uri = config['mongodb']['uri']
        self.port = config['mongodb']['port']
        self.user = config['mongodb']['user']
        self.password = config['mongodb']['password']
        self.database = config['mongodb']['database']
        self.collection = config['mongodb']['collection']
        self.collection_connection = MongoClient("{}:{}@{}".format(self.user, self.password), port=self.port)[self.database][self.collection]


    def save_item(self, video_id: str, key: str, content: Any):
        result = self.collection_connection.find_one({video_id: {"$exists": True}})
        if result:
            self.collection_connection.update_one(
                {video_id: {"$exists": True}},
                {"$set": {f"{video_id}.{key}": content}}
            )
        else:
            self.collection_connection.insert_one({video_id: content})

    def get_item(self, video_id: str) -> dict:
        result = self.collection_connection.find_one({video_id: {"$exists": True}})
        if result:
            return result[video_id]
        return None
