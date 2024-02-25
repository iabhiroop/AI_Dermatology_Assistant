from pymongo import MongoClient
from datetime import datetime

MONGODB_URI = "mongodb://localhost:27017"
DB_NAME = "dermadata"
MONGODB_COLLECTION = "chatdata"

class DB:
    def __init__(self):
        mongo_client = MongoClient(MONGODB_URI)
        ostello_ml_db = mongo_client[DB_NAME]

        self.db_client = ostello_ml_db[MONGODB_COLLECTION]

    def get_last_history(self, room_id, limit):
        return self.db_client.find_one({
            "roomid": room_id
        }, {
            "_id": 0,
            "roomid": 1,
            "history": {"$slice": -limit},
        })

    def get_room(self, room_id, limit, skip, chat_limit, chat_skip):
        if room_id is not None:
            rooms = self.db_client.find_one({
                "roomid": room_id
            }, {
                "_id": 0,
                "roomid": 1,
                "followUpQuestions": 1,
                "chat_count": {"$size": "$history"},
                "history": {"$slice": [{"$reverseArray": "$history"}, chat_skip, chat_limit]}
            })

            return rooms, 1
        else:
            count = self.db_client.count_documents({})
            rooms = self.db_client.find({}, {
                "_id": 0,
                "roomid": 1,
                "followUpQuestions": 1,
                "chat_count": {"$size": "$history"},
                "history": {"$slice": [{"$reverseArray": "$history"}, chat_skip, chat_limit]},
                "time_stamp":1,
            }).limit(limit).skip(skip)

            rooms_list = []

            for room_data in rooms:
                rooms_list.append(room_data)
            
            rooms_list = sorted(rooms_list, key=lambda x: x['time_stamp'],reverse=True)

            return rooms_list, count

    def create_room(self, data):
        return self.db_client.insert_one(data)

    def append_message_to_room(self, room_id, msg,time_stamp):
        for chat in msg:
            self.db_client.update_one({
                "roomid": room_id
            }, {
                "$push": {"history": chat, "conversation_history": chat},
                "$set": {"time_stamp": time_stamp}
            })

    def set_summary_to_room(self, room_id, follow_ups):
        return self.db_client.update_one({
            "roomid": room_id
        }, {
            "$set": {"followUpQuestions": follow_ups},
        })

    def set_follow_ups_to_room(self, room_id, follow_ups):
        return self.db_client.update_one({
            "roomid": room_id
        }, {
            "$set": {"followUpQuestions": follow_ups},
        })
        
db_client = DB()
