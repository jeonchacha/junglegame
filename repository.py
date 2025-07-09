from pymongo import MongoClient
from bson import ObjectId

client = MongoClient('localhost', 27017)
db = client.junglegame

def create_user(userdoc):
    db.user.insert_one(userdoc)

def find_id(id):
    return db.user.find_one({'id':id})

def store_refresh_token(tokendoc):
    db.token.insert_one(tokendoc)

def is_refresh_token_valid(jti):
    return db.token.find_one({'jti':jti})
