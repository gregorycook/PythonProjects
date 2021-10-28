from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
import os
import sqlite3
import uuid

app = Flask(__name__)
api = Api(app)


SERVER_ID = "1ffe3512-1def-4e1d-ae24-6a3ac31c6ff0"


def create_sqlite_db():
    if not os.path.isfile("crypto.db"):
        connection = sqlite3.connect("crypto.db")
        cursor = connection.cursor()
        try:
            cursor.execute('''CREATE TABLE user (id TEXT PRIMARY KEY, public_key BLOB, private_key BLOB)''')
        finally:
            connection.close()


def get_user(user_id):
    select_user_sql = "SELECT id, public_key, private_key FROM user WHERE id=:user_id"

    connection = sqlite3.connect("crypto.db")
    try:
        cursor = connection.cursor()
        cursor.execute(select_user_sql, {"user_id": user_id})

        users = cursor.fetchall()
    finally:
        connection.close()

    user = None
    if len(users) == 1:
        user = {
            "Id": users[0][0],
            "PublicKey": users[0][1].decode("utf-8"),
            "PrivateKey": users[0][2].decode("utf-8")
        }

    return user


class Generate(Resource):
    def post(self):
        # returns user_id
        # print(request.json["PublicKey"])
        create_sqlite_db()
        insert_user_sql = "INSERT INTO user (id, public_key, private_key) VALUES (?, ?, ?)"

        user_id = str(uuid.uuid4())

        private_key = None
        public_key = request.json["PublicKey"]

        connection = sqlite3.connect("crypto.db")
        try:
            cursor = connection.cursor()
            cursor.execute(insert_user_sql, [user_id, public_key, private_key])
            connection.commit()
        finally:
            connection.close()

        server_identity = get_user(SERVER_ID)

        return {
            "UserId": user_id,
            "ServerPublicKey": server_identity["PublicKey"]}


api.add_resource(Generate, '/generate')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")