from operator import imod
import os
from sqlite3 import Date
from flask import Flask, request
import requests
import socket
import json
import pymongo
import random
import string
from datetime import datetime

app = Flask(__name__)
data = {}


@app.route('/create-short-url', methods=['POST', 'GET'])
def create_short_url():
    url = request.form['u']
    while True:
        id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        if urls.find_one({"id":id}) == None:
            break
    
    urls.insert_one({"id":id,"url":url,"inserted_time":datetime.today()})
    return "service/" + id


@app.route('/go-to-short-url/<id>', methods=['GET'])
def go_to_short_url(id):
    url = urls.find_one({"id":id})
    if url is not None:
        return url['url']
    return 'Url Not Found'


if __name__ == '__main__':
    try:
        with open("config.json", "r") as config:
            data = json.load(config)
    #default configmap
    except FileNotFoundError:
        print("Entered default configmap")
        data["port"] = 8080
        data["hostname"] = "project_mongodb"
        data["expire_time"] = 45


    username = os.getenv('PYMONGO_USERNAME')
    password = os.getenv('PYMONGO_PASSWORD')

    #default secret
    if username is None or password is None:
        print("Entered default secret")
        username = "admin"
        password = "password"

    client = pymongo.MongoClient(host=data['hostname'],port=27017,username=username,password=password,authSource="admin")
    db = client['shortUrlDB']
    urls = db['urls']
    try:
        urls.create_index("inserted_time",expireAfterSeconds=data['expire_time'])
    except Exception as e:
        print(e)

    app.run(host='0.0.0.0', debug=True, port=data["port"])
