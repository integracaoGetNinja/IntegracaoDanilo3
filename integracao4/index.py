from flask import Flask, request, json, jsonify
import requests
from pymongo import MongoClient

client = MongoClient('mongodb+srv://integracaoDanilo4:8iz8NbjUfoUSxAQG@cluterb.ypmgnks.mongodb.net/')
db = client["credencialIntegracao4Danilo"]
col_bling = db["col_bling"]

app = Flask(__name__)


@app.route("/")
def index():
    return jsonify({"status": "ON"})


@app.route("/callback")
def callback():
    payload = request.args
    code = payload.get("code")

    payload = json.dumps({
        "grant_type": "authorization_code",
        "code": code
    })
    headers = {
        'Authorization': 'Basic ZjJlNzhhNjkzYTBmN2I5ZDE3Yjg1ZTA4MzQxYzY1NTM5NzhiYjY4MDo5OTk0OTQ4ZjY5NzExZTJhMTFjMTlkOGY1NTk3NWE2MjhhNmM5YzgzYzQyOTVjNzdmZTQwNjQ2ODVkYzY=',
        'Content-Type': 'application/json',
        'Cookie': 'PHPSESSID=f4aa8gc0a6kr70ag2qfbi8iu1k'
    }
    response = requests.request("POST", "https://www.bling.com.br/Api/v3/oauth/token", headers=headers, data=payload)

    if not col_bling.find_one({"_id": 0}):
        col_bling.insert_one(
            {
                "_id": 0,
                "token": response.json()["access_token"]
            }
        )
    else:
        col_bling.update_one(
            {"_id": 0},
            {"$set": {"token": response.json()["access_token"]}}
        )
    return jsonify(
        {
            "msg": "token gerado com sucesso!",
            "token": response.json()["access_token"]
        }
    )


@app.route("/token")
def token():
    return col_bling.find_one({"_id": 0}).get('token')


if __name__ == "__main__":
    app.run()
