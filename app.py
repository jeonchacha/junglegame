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
import uuid

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

def create_access_token(user_id):
    encoded = jwt.encode(
        payload={
            'user_id': user_id,
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=10)
        },
        key=app.config['SECRET_KEY'],
        algorithm='HS256'
    )
    return encoded

def create_refresh_token(user_id):
    jti = str(uuid.uuid4())
    encoded = jwt.encode(
        payload={
            'jti': jti,
            'user_id': user_id,
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
        },
        key=app.config['SECRET_KEY'],
        algorithm='HS256'
    )
    
    tokendoc = {
        'jti': jti,
        'user_id':user_id,
        'revoke': False
    }
    # db 저장
    store_refresh_token(tokendoc)

    return encoded

# 엑세스 토큰 재발급
    # 리프레시 토큰이 존재하는지, 존재했으나 만료되지 않았는지, 토큰이 유효한지(해당유저에 해당하는건지), 블랙리스트가 아닌지( 이것만 디비)
    # 리프레시 토큰을 디비에서 관리하는데 쿠키에 있어야할 이유?
        # 모든 경우 db 접근할 필요없음. 디비에 접근해야 하는경우만 하고 나머지는 쿠키에서 가져와서 유효성 검사 하는게 나음.
        # db에 접근해야 하는 경우 -> 로그아웃시 블랙리스트, 재발급 할때 블랙리스트 인지 조회할때 사용
                # 등록 , 업데이트, 조회
    # 리프레시 토큰까지 만료되면 그냥 재로그인..
    # 디비에 아이디랑 블랙리스트만 있으면 되지않나..
    # 아 아이디로 하면 안댐 uuid 써야한다., 아이디로 하면 중복나오잖아
@app.route('/refresh', methods=['POST'])
# 모든 403 에는 재 로그인 시킬 것
def refresh():
    refresh_token = request.cookies.get('refresh_token')
    if not refresh_token:
        return jsonify({'msg': '리프레시 토큰이 존재하지 않습니다.'}), 403
    try:
        payload = jwt.decode(refresh_token, app.config['SECRET_KEY'], algorithms=['HS256'])
        jti = payload['jti']

        # 블랙리스트 인지 조회
        is_blacklist = is_refresh_token_valid(jti)
        if is_blacklist['revoke']:
            return jsonify({'msg': '리프레시 토큰이 revoke 되었습니다.'}), 403
        
        new_access_token = create_access_token(payload['user_id'])
        response = make_response(jsonify({'result':'엑세스 토큰 재발급 완료'}))
        response.headers['Authorization'] = f'Bearer {new_access_token}'
        return response
    
    except jwt.ExpiredSignatureError:
        return jsonify({'msg': '리프레시 토큰이 만료됐습니다.'}), 403    
    except jwt.InvalidTokenError:
        return jsonify({'msg': '리프레시 토큰이 유효하지 않습니다.'}), 403

# 로그아웃 구현 쿠키의 리프래시토큰을 블랙리스트 처리하고 쿠키제거까지


# 토큰 검증 데코레이터
def verify_token(f):
    @wraps(f)
    # 모든 403 에는 엑세스 토큰 재발급
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'msg': '엑세스 토큰이 존재하지 않습니다.'}), 403
        try:
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = payload['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'msg': '엑세스 토큰이 만료됐습니다.'}), 403
        except jwt.InvalidTokenError:
            return jsonify({'msg': '엑세스 토큰이 유효하지 않습니다.'}), 403
        
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
        access_token = create_access_token(user['id'])
        refresh_token = create_refresh_token(user['id'])

        response = make_response(jsonify({'result':'success', 'userinfo':user}))
        response.headers['Authorization'] = f'Bearer {access_token}'
        response.set_cookie('refresh_token', refresh_token, httponly=True, samesite='Strict')
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