from pymongo import MongoClient
from typing import Any
from utils.config import Collections
from schemas.video import Video
class MongoConnection:
    def __init__(self, config: dict) -> None:
        self.host = config['mongodb']['host']
        self.port = config['mongodb']['port']
        self.user = config['mongodb']['username']
        self.password = config['mongodb']['password']
        self.database = config['mongodb']['database']
        self.video_collection = config['mongodb'][Collections.videos.value]
        self.voice_collection = config['mongodb'][Collections.voices.value]
        print("mongodb://{}:{}@{}".format(self.user, self.password, self.host))
        self.database = MongoClient("mongodb://{}:{}@{}".format(self.user, self.password, self.host))[self.database]
# mongodb://root:password@172.20.0.2:27017/

    def save_video(self, video: Video):
        self.save_item(video.video_id, Collections.videos, video.model_dump())

    def save_item(self, video_id: str, collection: Collections, content: Any):
        if collection == Collections.videos:
            conn_collection = self.database[self.video_collection]
        elif collection == Collections.voices:
            conn_collection = self.database[self.voice_collection]

        result = conn_collection.find_one({video_id: {"$exists": True}})
        if result:
            conn_collection.update_one(
                {video_id: {"$exists": True}},
                {"$set": {f"{video_id}": content}}
            )
        else:
            conn_collection.insert_one({video_id: content})

    def get_video(self, video_id: str) -> Video:
        return  Video.from_dict(self.get_item(video_id, Collections.videos))
    
    def get_item(self, item_id: str, collection: Collections) -> dict:
        if collection == Collections.videos:
            conn_collection = self.database[self.video_collection]
        elif collection == Collections.voices:
            conn_collection = self.database[self.voice_collection]
        result = conn_collection.find_one({item_id: {"$exists": True}})
        if result:
            return result[item_id]
        return None
