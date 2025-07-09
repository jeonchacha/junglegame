from bson import ObjectId
from flask import Flask, jsonify, render_template, request, make_response
from flask.json.provider import JSONProvider
from repository import *
import json
import sys
import jwt
import datetime
import bcrypt
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'

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

def create_token(user_id):
    encoded = jwt.encode(
        payload={
            'user_id': user_id,
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=1)
            },
        key=app.config['SECRET_KEY'],
        algorithm='HS256'
        )
    return encoded

# 토큰 검증 데코레이터
def verify_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'msg': '토큰이 존재하지 않습니다.'}), 403
        try:
            token = auth_header.split(" ")[1]
            decode_jwt = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = decode_jwt['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'msg': '토큰이 만료됐습니다.'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'msg': '토큰이 유효하지 않습니다.'}), 403
        
        return f(current_user_id, *args, **kwargs)
    return decorated

@app.route('/protected', methods=['GET'])
@verify_token
def protected(current_user_id):
    return current_user_id

@app.route('/login', methods=['POST'])
def login():
    id = request.form['id']
    pw = request.form['pw']

    encoded_pw = pw.encode('utf-8')

    user = find_id(id)
    
    if user != None and bcrypt.checkpw(encoded_pw, user['pw']):
        user.pop('pw')
        encoded_jwt = create_token(user['id'])

        response = make_response(jsonify({'result':'success', 'userinfo':user}))
        response.headers['Authorization'] = f'Bearer {encoded_jwt}'
        return response   
    else:
        return jsonify({'result':'failure', 'msg':'아이디가 존재하지 않거나 비밀번호가 틀렸습니다.'})

@app.route('/signup', methods=['POST'])
def signup():
    name = request.form['name']
    id = request.form['id']
    pw = request.form['pw']
    id_github = request.form['id_github']

    # 바이트 문자열로 변환
    encoded_pw = pw.encode('utf-8')
    # 동일한 입력에 대해서도 항상 다른 값 
    salt = bcrypt.gensalt()
    hashed_pw = bcrypt.hashpw(encoded_pw, salt)

    userdoc = {
        'name':name,
        'id':id,
        'pw':hashed_pw,
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