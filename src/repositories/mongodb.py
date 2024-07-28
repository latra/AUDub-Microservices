from pymongo import MongoClient
from typing import Any


class MongoConnection:
    def __init__(self, config: dict) -> None:
        self.host = config['mongodb']['host']
        self.port = config['mongodb']['port']
        self.user = config['mongodb']['username']
        self.password = config['mongodb']['password']
        self.database = config['mongodb']['database']
        self.collection = config['mongodb']['collection']
        print("mongodb://{}:{}@{}".format(self.user, self.password, self.host))
        self.collection_connection = MongoClient("mongodb://{}:{}@{}".format(self.user, self.password, self.host))[self.database][self.collection]
# mongodb://root:password@172.20.0.2:27017/

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
