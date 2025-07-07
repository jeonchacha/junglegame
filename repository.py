from pymongo import MongoClient
from bson import ObjectId

client = MongoClient('localhost', 27017)
db = client.jungle