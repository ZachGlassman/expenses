import pymongo
from datetime import datetime

def _sort_by_date(x):
    date = [(datetime.strptime(i['date'], "%Y-%m-%d"), i) for i in x]
    return [i[1] for i in sorted(date, key=lambda x : x[0], reverse=True)]
    
class MongoDatabase(object):
    def __init__(self, url):
        self.client = pymongo.MongoClient(url)
        self.db = self.client.get_default_database()

    def get_collection(self, name, sort_date=False, num=None):
        docs = self._get_collection(name, num)
        return _sort_by_date(docs) if sort_date else docs

    def _get_collection(self, name, num=None):
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