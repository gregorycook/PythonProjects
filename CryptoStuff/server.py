from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
import sqlite3

app = Flask(__name__)
api = Api(app)

class Generate(Resource):
    def post(self):
        print(request)
        print(request.json)
        return {'hello': 'world'}

api.add_resource(Generate, '/generate')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")