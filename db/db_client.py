from pymongo import MongoClient


class MongoConnection(object):

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client['db']

    def get_collection(self, name):
        self.collection = self.db[name]


class MyCollection(MongoConnection):

    def __init__(self):
       super(MyCollection, self).__init__()
       self.get_collection('collection_name')

    def update_and_save(self, obj):
       if self.collection.find({'id': obj.id}).count():
           self.collection.update({"id": obj.id}, {'id': 123, 'name': 'test'})
       else:
           self.collection.insert_one({'id':123,'name':'test'})

    def remove(self, obj):
        if self.collection.find({'id': obj.id}).count():
           self.collection.delete_one({ "id": obj.id})

