import pymongo
class MongoDatabase(object):
    def __init__(self, url):
        self.client = pymongo.MongoClient(url)
        self.db = self.client.get_default_database()

    def get_collection(self, name, num=None):
        """get a collection"""
        result = []
        for i, ele in enumerate(self.db[name].find()):
            result.append(ele)
            if num is not None:
                if i > num:
                    return result

        return result

    def put(self, collection, data):
        self.db[collection].insert(data)