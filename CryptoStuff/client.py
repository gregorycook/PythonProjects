import json
import os
import requests
import sqlite3
import sys

from Crypto.PublicKey import RSA

KEY_LENGTH = 2048

GENERATE_ENDPOINT = "HTTP://192.168.0.150:5000/generate"
CONFIG_FILE = "crypto_client.json"


def usage():
    print("Usage:")
    print("--generate, generates keypair and registers with server")


def generate():
    if not os.path.isfile(CONFIG_FILE):
        # generate key pair
        key = RSA.generate(KEY_LENGTH)
        private_key = key.export_key('PEM').decode("utf-8")
        public_key = key.publickey().exportKey('PEM').decode("utf-8")

        # send public key to server and retrieve user_id
        headers = {"content-type": "application/json"}
        payload = dict()
        payload["PublicKey"] = public_key

        response = requests.post(GENERATE_ENDPOINT, data=json.dumps(payload), headers=headers)

        response_json = json.loads(response.text)
        user = json.dumps({
            "UserId": response_json["UserId"],
            "PublicKey": public_key,
            "PrivateKey": private_key,
            "KeyLength": KEY_LENGTH,
            "ServerPublicKey": response_json["ServerPublicKey"]})

        with open(CONFIG_FILE, 'w') as outfile:
            json.dump(user, outfile)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        usage()
        quit()

    arg_index = 1
    do_generate = False
    while arg_index < len(sys.argv):
        if sys.argv[arg_index] == "--generate":
            do_generate = True
            arg_index += 1

    if do_generate:
        generate()


