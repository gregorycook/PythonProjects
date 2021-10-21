import requests
import sys

from Crypto.PublicKey import RSA

KEY_LENGTH = 2048

GENERATE_ENDPOINT = "HTTP://192.168.0.43:5000/generate"


def usage():
    print("Usage:")
    print("--generate, generates keypair and registers with server")


def generate():
    # generate key pair
    key = RSA.generate(KEY_LENGTH)
    private_key = key.export_key('PEM')
    public_key = key.publickey().exportKey('PEM')


    # send public key to server and retrieve user_id
    payload = {}
    payload["PublicKey"] = public_key
    response = requests.post(GENERATE_ENDPOINT, data=payload)
    print(response)
    # save private key and user_id to file
    return


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


