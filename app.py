from bson import ObjectId
from flask import Flask, jsonify, render_template, request
from flask.json.provider import JSONProvider
from repository import *
import json
import sys

app = Flask(__name__)

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

class CustomJSONProvider(JSONProvider):
    def dumps(self, obj, **kwargs):
        return json.dumps(obj, **kwargs, cls=CustomJSONEncoder)

    def loads(self, s, **kwargs):
        return json.loads(s, **kwargs)

app.json = CustomJSONProvider(app)

@app.route('/')
def home():
   return render_template('index.html')

@app.route('/login', methods=['GET'])
def login():
    id = request.form['id']
    pw = request.form['pw']

    user = find_user(id, pw)

    if user != None:
        return jsonify({'result':'success', 'userinfo':user})    
    else:
        return jsonify({'result':'failure', 'msg':'아이디가 존재하지 않거나 비밀번호가 틀렸습니다.'})

@app.route('/signup', methods=['POST'])
def signup():
    name = request.form['name']
    id = request.form['id']
    pw = request.form['pw']
    id_github = request.form['id_github']

    userdoc = {
        'name':name,
        'id':id,
        'pw':pw,
        'id_github':id_github
    }

    create_user(userdoc)

    return jsonify({'result':'success'})

@app.route('/checkid', methods=['GET'])
def checkid():

    id = request.args.get('id')
    user = find_id(id)

    if user != None:
        return jsonify({'result':'failure', 'msg':user['id'] + ' 는 중복된 아이디 입니다.'})
    else:
        return jsonify({'result':'success', 'msg':id + ' 는 사용가능한 아이디 입니다.'})

if __name__ == '__main__':
   print(sys.executable)  
   app.run('0.0.0.0', port=5001, debug=True)