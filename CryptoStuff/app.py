from flask import Flask, jsonify, request
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
import sqlite3

app = Flask(__name__)

@app.route("/")
def hello_world():
	return "<center>Hello World!</center>"

incomes = [
  { 'description': 'salary', 'amount': 5000 }
]

private_key = "-----BEGIN RSA PRIVATE KEY----- MIICXAIBAAKBgQDbgwWI2y2VKeY56xrEOUlKgigmi4H5BeA090GmgRBW2MUglYtW 76EHfjfvPNPZwRKaszhV/3FNJLzDWBhJS4tLO5pKDYDu0LxaNwzFkrgSjsb0kdbW bdJGqj78wR6KutBd6ItgU14mfOnTuW7q6VhoYZ4FvWkqXd30luRPEWf4QwIDAQAB AoGAIZGOTvOnALNzyTH/xGKMUjrISr4KhhtUwlTOMy5z4gwWopkr7K4K6UXvO4SI /eO4OsnN2NzjpevzJUkQtw4N7WPjPhEGK7JkrfKMm6ekjID1Aa0NdU+bUk/SjK5M X8r3GnrNij99Gjdj19cngmavGBlJ6qftqQzIdhVhn2F3g40CQQDej0iIxCIwYYlA VmPdZy69NqmhcReAsB/SJrXY0FpZ6Hi30qwBjtKzRrv1SNC39wfAhM9+TfykAmHI ELJE8+aNAkEA/H6AYaObn8DdusTrTdWkxNWSTS4quelKPUNPGRVXARUfCSMkb+8A Bt8ePusc23PcAKbQIvUyOAU6x+ud1/jODwJATrbolY6g9PGaRIoJegYDbuKFblb8 VAR2zLHqQQu32PKyt3koYsir1sJeuesN/vK86CdQ58AXab557POSyXZmBQJBAPmX 0zCxmlUBQi4uGqyGVKp+tHC3AmVkx45nyvjwr2DSkCtoIczEZTJlvHBV2eDVVtUO ERF9cHcQNFsL/qxPtuECQAKmlV/it7ApdI712WmDPn8uAwNO4B1YfbNCf2tGL/gb tVxl7QcqPGcL09zAeb/fAFSkLlRGa/7wUOwcTV5wNOo= -----END RSA PRIVATE KEY-----"
public_key = "-----BEGIN PUBLIC KEY----- MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDbgwWI2y2VKeY56xrEOUlKgigm i4H5BeA090GmgRBW2MUglYtW76EHfjfvPNPZwRKaszhV/3FNJLzDWBhJS4tLO5pK DYDu0LxaNwzFkrgSjsb0kdbWbdJGqj78wR6KutBd6ItgU14mfOnTuW7q6VhoYZ4F vWkqXd30luRPEWf4QwIDAQAB -----END PUBLIC KEY-----"

@app.route('/incomes', methods=['POST'])
def get_incomes():
	print(request.json)
	incomes[0]["description"] = request.json["fish"]
	return jsonify(incomes)

key_result={"key": ""}

@app.route('/generate-key', methods=['POST'])
def generate_key():
	key = RSA.generate(1024)
	key_result["private_key"] = key.export_key('PEM').decode("utf-8")
	key_result["public_key"] = key.publickey().export_key().decode("utf-8")
	return jsonify(key_result)

@app.route('/crypt', methods=['POST'])
def crypt():
	key_type = request.json["key_type"]
	message = request.json["message"]
	user_id = request.json["user_id"]

	# data = "I met aliens in UFO. Here is the map.".encode("utf-8")
	data = message.encode("utf-8")

	# recipient_key = RSA.import_key(open("receiver.pem").read())
	recipient_key = RSA.import_key(public_key)
	session_key = get_random_bytes(16)

	# Encrypt the session key with the public RSA key
	cipher_rsa = PKCS1_OAEP.new(recipient_key)
	enc_session_key = cipher_rsa.encrypt(session_key)

	# Encrypt the data with the AES session key
	cipher_aes = AES.new(session_key, AES.MODE_EAX)
	ciphertext, tag = cipher_aes.encrypt_and_digest(data)

	result = {}
	result["enc_session_key"] = enc_session_key
	result["nonce"] = nonce
	result["tag"] = tag
	result["ciphertext"] = ciphertext

	return jsonify(result)

def create_sqlite_db():
	if not os.path.isfile("users.db"):
		connection = sqlite3.connect("users.db")
		cursor = connection.cursor()
		cursor.execute('''CREATE TABLE User (id TEXT PRIMARY KEY, public_key TEXT, private_key TEXT)''')



if __name__ == "__main__":
	app.run(debug=True, host="0.0.0.0")

