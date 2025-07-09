<<<<<<< Updated upstream
from bson import ObjectId
from flask import Flask, jsonify, render_template, request
=======
from flask import Flask, jsonify, render_template, request, redirect, url_for, make_response
>>>>>>> Stashed changes
from flask.json.provider import JSONProvider
from repository import *
import json
import sys
<<<<<<< Updated upstream
=======
import jwt
import bcrypt
from functools import wraps

import random
import datetime

import schedule
import time
import threading
import uuid
>>>>>>> Stashed changes

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

<<<<<<< Updated upstream
@app.route('/')
def home():
   return render_template('index.html')
=======
# 1회차 = 7월 7일 (기준)
firstRound = datetime.date(2025, 7, 7)

def create_token(user_id):
    now = datetime.datetime.now(datetime.timezone.utc)
    exp = now + datetime.timedelta(hours=10)

    payload = {
        'user_id': user_id,
        'exp': exp,
        'iat': now,
        'jti': str(uuid.uuid4())  # 유일한 ID 부여 → 토큰이 매번 다르게 나옴
    }

    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token

# 토큰 검증 데코레이터
def verify_token(f):
    @wraps(f)

    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        print(auth_header)
        if not auth_header:
            print("❌ 토큰이 없습니다.")
            return jsonify({'msg': '토큰이 존재하지 않습니다.'}), 403

        parts = auth_header.split(" ")
        if len(parts) != 2 or parts[0] != 'Bearer':
            print("❌ 잘못된 토큰 형식:", auth_header)
            return jsonify({'msg': '잘못된 토큰 형식입니다.'}), 403

        token = parts[1]
        try:
            decode_jwt = jwt.decode(
                token,
                app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            current_user_id = decode_jwt['user_id']

        except jwt.ExpiredSignatureError:
            print("⏰ 토큰 만료됨")
            return jsonify({'msg': '토큰이 만료됐습니다.'}), 401
        except jwt.DecodeError as e:
            print("❌ 디코딩 오류:", str(e))
            return jsonify({'msg': '토큰 디코딩 실패'}), 403
        except jwt.InvalidTokenError as e:
            print("❌ 토큰 검증 실패:", str(e))
            return jsonify({'msg': '유효하지 않은 토큰입니다.'}), 403
        except Exception as e:
            print("❌ 기타 예외:", str(e))
            return jsonify({'msg': '서버 오류 발생'}), 500

        return f(current_user_id, *args, **kwargs)
    return decorated


# Flask-Mail 설정
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'seo980620@gmail.com'
app.config['MAIL_PASSWORD'] = 'hhvw vlgp neca mtyk'
app.config['MAIL_DEFAULT_SENDER'] = 'seo980620@gmail.com'
mail = Mail(app)

#이메일 발송 함수
def send_verification_email(user_email, code):
    msg = Message(
        subject = "[Flask App] 이메일 주소 확인 코드",
        recipients=[user_email],
        html=f"""
        <h1>이메일 주소 확인</h1>
        <p>계속하려면 6자리 코드를 입력해주세요</p>
        <h2>{code}</h2>
        <p>이 코드는 5분간 유효합니다.</p>
        """
    )
    mail.send(msg)

def makeTestUser():
    name = 'userName'
    id = 'userId22'
    pw = '1q2w3e4r'
    encodedPw = pw.encode('utf-8')
    salt = bcrypt.gensalt()
    hashedPw = bcrypt.hashpw(encodedPw, salt)

    githubAccount = 'userGithubAccount'
    appTicket = 1
    getAppTicket = False
    appList = [{'productName': '콜라', 'appPrice': 10, 'appDate': datetime.datetime(2025,7,6)},
                {'producctName': '사이다', 'appPrice': 20,'appDate': datetime.datetime(2025,7,7)}]
    attendanceList = [{'dateTime': datetime.datetime(2025,7,6), 'isAttendance': True},
                      {'dateTime': datetime.datetime(2025,7,7), 'isAttendance': True},
                      {'dateTime': datetime.datetime(2025,7,8), 'isAttendance': True}]
    
    user = {'name': name, 'id': id, 'pw': hashedPw, 'githubAccount': githubAccount,
                'appTicket': appTicket, 'getAppTicket': getAppTicket, 'appList': appList, 'attendanceList': attendanceList}
    db.user.insert_one(user)

def makeRandomProduct():
    productName = "productName"
    minPrice = 10
    maxPrice = 20
    appStartDate = datetime.datetime.now()
    appEndDate = datetime.datetime.today().replace(hour=23, minute=59, second=59, microsecond=0)

    appUsers = []
    for i in range(5):
        userid = i
        appPrice = random.randint(minPrice, maxPrice)
        appUsers.append({'id': userid, 'appPrice': appPrice})

    product = {'productName': productName, 'minPrice': minPrice, 'maxPrice': maxPrice, 
                'appStartDate': appStartDate, 'appEndDate': appEndDate, 'appUsers': appUsers}
    db.product.insert_one(product)

def selectWinner():
    appEndDate = datetime.datetime.today().replace(hour=23, minute=59, second=59, microsecond=0)
    product = db.product.find_one({'appEndDate': appEndDate})
    productName = product['productName']

    appUsers = product['appUsers']
    appPriceList = [item['appPrice'] for item in appUsers]
    
    appLog = []
    priceCounts = Counter(appPriceList)
    for price, count in priceCounts.items():
        appLog.append({'price': price, 'count': count})

    #최소면서 중복되지 않는 수 찾기
    unique_prices = []
    for item in appLog:
        if item['count'] == 1:
            unique_prices.append(item['price'])

    if(unique_prices):
        appPrice = min(unique_prices)
        appUser = next((item['id'] for item in appUsers if item['appPrice'] == appPrice), None)

    else:
        appPrice = None
        appUser = None

    appRound = (datetime.date.today() - firstRound).days + 1

    reward = {'productName': productName, 'appPrice': appPrice, 'appUser': appUser, 'appRound': appRound, 'appLog': appLog}
    db.reward.insert_one(reward)

def run_scheduler():
    # schedule.run_pending()을 계속 실행하는 루프.
    while True:
        schedule.run_pending()
        time.sleep(1) # 1초마다 예약된 작업이 있는지 확인

def start_scheduler():
    # 테스트용 5초마다 함수실행
    # schedule.every(5).seconds.do(makeRandomProduct)

    # 매일 23시 59분 59초에 selectWinner 함수 실행
    schedule.every().day.at("23:59:59").do(selectWinner)
    # 매일 0시 0분 0초에 미출석 기록
    schedule.every().day.at("00:00:00").do(pushAttendance)

    # 스케줄러를 별도의 스레드에서 실행
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True # 메인 스레드가 종료되면 함께 종료되도록 설정
    scheduler_thread.start()


#경품리스트페이지 주기
@app.route('/getRewards', methods=['GET'])
def getRewards():
    all_doc_cursor = db.reward.find({})
    rewards = list(all_doc_cursor)
    #appRound로 정렬해서 주기
    #내림차순
    sorted_rewards = sorted(rewards, key=lambda reward: reward['appRound'], reverse=True)
    return render_template('reward.html',
                            rewards=sorted_rewards)

@app.route('/', methods=['GET'])
def home():
    return render_template('login.html')

@app.route('/join')
def join():
    return render_template("join.html")

@app.route('/mainPage',methods=['GET'])
def main_Page():
    return render_template("main.html")

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        id = request.form['id']
        pw = request.form['pw']

        encoded_pw = pw.encode('utf-8')

        user = find_id(id)
        
        if user != None and bcrypt.checkpw(encoded_pw, user['pw']):
            user.pop('pw')
            encoded_jwt = create_token(user['id'])

            response = make_response(jsonify({'result':'success'}))
            response.headers['Authorization'] =encoded_jwt
            return response
        else:
            return jsonify({'result':'failure', 'msg':'아이디가 존재하지 않거나 비밀번호가 틀렸습니다.'})
        
    else:
        return render_template("login.html")

@app.route('/main', methods=['GET'])
@verify_token
def main(current_user_id):
    print('start')
    user = db.user.find_one({'id': current_user_id})
    #appList
    appList = user.get('appList', [])
    for app in appList:
        app['appDate'] = app['appDate'].isoformat()

    #consecutiveDay, attendanceList
    consecutiveDay = calcConsecutiveAttendance(user)
    #줘야되는 형식[{'dateTime': datetime,'level': int}]
    atdList = user.get('attendanceList', [])
    if atdList:
        attendanceList = [
            {
                'dateTime': item['dateTime'].isoformat(),
                'level': int(item['isAttendance'])
            }
            for item in atdList
        ]
    else:
        attendanceList = []

    #appTicket
    appTicket = user.get('appTicket', 0)

    #productName(나중에 이미지로), minPrice, maxPrice
    #응모 마감일이 오늘 23:59:59.999999 = 현재 회차 상품
    endDate = datetime.datetime.today().replace(hour=23, minute=59, second=59, microsecond=0)
    product = db.product.find_one({'appEndDate': endDate})
    productName = product['productName']
    minPrice = product['minPrice']
    maxPrice = product['maxPrice']
    
    return render_template("main.html",result="success",
                           appList=appList, consecutiveDay=consecutiveDay, attendanceList=attendanceList, appTicket=appTicket,
                           productName=productName, minPrice=minPrice, maxPrice=maxPrice)

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
    
#@app.route('/register', methods=['GET', 'POST'])
#def register():
    if request.method == 'POST':
        email = request.form.get('email')
        id = request.form.get('id')
        pw = request.form.get('password')

        code = str(random.randint(100000,999999))
        expiration_time = datetime.datetime.now() + datetime.timedelta(minutes=5)

        user = {'email': email, 'id': id, 'pw': pw, 'code': code, 'code_expires_at': expiration_time}

        db.user.insert_one(user)
        send_verification_email(email, code)

        return render_template('register.html')
        # return redirect(url_for('verify-email', email=email))
    
    return render_template('register.html')

#@app.route('/verify-email', methods=['GET'])
#def verifyEmail():
    code = request.args.get('code')
    return jsonify({'result': 'success'})

#응모하기
@app.route('/apply', methods=['POST'])
@verify_token
def apply(current_user_id):
    appPrice = request.form.get('appPrice')
    user = db.user.find_one({'id': current_user_id})

    #응모권 부족한 경우
    if user['appTicket'] < 0:
        return jsonify({'resuslt': 'failure'})
    
    #티켓사용및 출석처리
    newAppTicket = user['appTicket'] - 1
    db.user.update_one({'id': id}, {'$set' : {'appTicket': newAppTicket}})
    newAttendanceList = user['attendanceList']
    for record in newAttendanceList:
        if record['datetime'] == datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0):
            record['isAttendance'] = True
            isAttendance = True
            break
    db.user.update_one({'id': id}, {'$set' : {'attendanceList': newAttendanceList}})

    #출석시 연속 응모 4배수에 추가 도전권 지급
    if isAttendance:
        consecutiveDay = calcConsecutiveAttendance(user)
        if (consecutiveDay % 4 == 0):
            newAppTicket = user['appTicket'] + 1
            db.user.update_one({'id': id}, {'$set' : {'appTicket': newAppTicket}})

    #응모 딕셔너리 만들어서 DB내 리스트에 추가
    endDate = datetime.datetime.today().replace(hour=23, minute=59, second=59, microsecond=0)
    product = db.product.find_one({'appEndDate': endDate})
    app = {'productName': product['productName'], 'appPrice': appPrice, 'appDate': datetime.datetime.now()}
    db.user.update_one({'id': id}, {'$push' : {'appList': app}})

    return jsonify({'result': 'success'})

#user DB받아서 연속 출석일 계산하기
def calcConsecutiveAttendance(user):
    attendanceList = user.get('attendanceList', [])
    if not attendanceList:
        return 0

    attendanceList.sort(key=lambda x: x['dateTime'])
    
    lastAttendedDay = datetime.datetime.today()
    consecutiveDay = 1
    for i, record in enumerate(attendanceList):
        currentDate = record['dateTime']

        if record['isAttendance']:
            if (currentDate - lastAttendedDay).days == 1:
                consecutiveDay += 1
            elif (currentDate - lastAttendedDay).days > 1:
                consecutiveDay = 1
            lastAttendedDay = currentDate

    return consecutiveDay

def pushAttendance():
    newAttendance = {'dateTime': datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0), 'isAttendance': True}
    db.user.update_many({}, {'$push' : {'attendanceList': newAttendance}})

#응모리스트받기 ~도전 기록~
@app.route('/getApplist', methods=['GET'])
@verify_token
def getApplist(current_user_id):
    user = db.user.find_one({'id': current_user_id})
    appList = user['appList']
    # datetime을 isoformat 문자열로 교체
    # datetime은 json 객체에 담을 수 없음!!!
    for app in appList:
        app['appDate'] = app['appDate'].isoformat()

    return jsonify({'result': 'success', 'appList': appList})

#연속응모횟수받기
@app.route('/getConsecutiveDay', methods=['GET'])
@verify_token
def getConsecutiveDay(current_user_id):
    user = db.user.find_one({'id': current_user_id})
    consecutiveDay = calcConsecutiveAttendance(user)
    #줘야되는 형식[{'dateTime': datetime,'level': int}]
    attendanceList = user['attendanceList']
    newAttendanceList = [
        {
            'dateTime': item['dateTime'].isoformat(),
            'level': int(item['isAttendance'])
        }
        for item in attendanceList
    ]

    return jsonify({'result': 'success', 'consecutiveDay': consecutiveDay, 'attendanceList': newAttendanceList})

#도전권 개수 받기
@app.route('/getTicketCount', methods=['GET'])
@verify_token
def getTicketCount(current_user_id):
    user = db.user.find_one({'id': current_user_id})
    appTicket = user['appTicket']
    return jsonify({'result': 'success', 'appTicket': appTicket})

#현재회차 상품정보 받기
@app.route('/getProductInfo', methods=['GET'])
def getProductInfo():
    # 응모 마감일이 오늘 23:59:59.999999 = 현재 회차 상품
    endDate = datetime.datetime.today().replace(hour=23, minute=59, second=59, microsecond=0)
    product = db.product.find_one({'appEndDate': endDate})
    productName = product['productName']
    minPrice = product['minPrice']
    maxPrice = product['maxPrice']
    return jsonify({'result': 'success', 'productName': productName, 'minPrice': minPrice, 'maxPrice': maxPrice})

def testGithub():
    userId = 'userId'
    user = db.user.find_one({'id': userId})
    githubAccount = user['githubAccount']
    req = requests.get(f'http://github.com/{githubAccount}')
    html = req.text

    soup = BeautifulSoup(html, 'html.parser')
    repos = soup.select('.ContributionCalendar-grid.js-calendar-graph-table')

    return jsonify({'result': 'success', 'repos': str(repos)})
    
@app.route('/test', methods=['GET'])
def test():
    makeTestUser()

    return jsonify({'result': 'success'})
>>>>>>> Stashed changes

if __name__ == '__main__':
   print(sys.executable)  
   app.run('0.0.0.0', port=5001, debug=True)