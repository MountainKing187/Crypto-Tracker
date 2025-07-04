from pymongo import MongoClient

class MongoHandler:
    def __init__(self):
        self.client = None
        self.db = None
    
    def init_app(self, app):
        self.client = MongoClient(app.config['MONGODB_URI'])
        self.db = self.client[app.config['MONGO_DB_NAME']]
    
    def get_collection(self, collection_name):
        return self.db[collection_name] if self.db else None
