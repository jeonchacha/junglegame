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

if __name__ == '__main__':
   print(sys.executable)  
   app.run('0.0.0.0', port=5001, debug=True)