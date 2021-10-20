import os
import sqlite3
import uuid

from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes

def generate_key_pair():
    keyPair = RSA.generate(3072)

    pubKey = keyPair.publickey()
    print(f"Public key:  (n={hex(pubKey.n)}, e={hex(pubKey.e)})")
    pubKeyPEM = pubKey.exportKey()
    print(pubKeyPEM.decode('ascii'))

    print(f"Private key: (n={hex(pubKey.n)}, d={hex(keyPair.d)})")
    privKeyPEM = keyPair.exportKey()
    print(privKeyPEM.decode('ascii'))


def rsa_encrypt_decrypt():
    key = RSA.generate(2048)
    private_key = key.export_key('PEM')
    print("private key is: {}".format(private_key))
    public_key = key.publickey().exportKey('PEM')
    print("public key is: {}".format(public_key))
    message = "This is a test message.  Hurray!"
    message = str.encode(message)

    rsa_public_key = RSA.importKey(public_key)
    rsa_public_key = PKCS1_OAEP.new(rsa_public_key)
    encrypted_text = rsa_public_key.encrypt(message)


def crypt():
    data = "Here fishy fishy fishy!"
    print("0 {}", data.encode("ascii"))
    key = RSA.generate(2048)
    private_key = key.export_key('PEM')
    print("private key is: {}".format(private_key))
    public_key = key.publickey().exportKey('PEM')
    print("public key is: {}".format(public_key))

    # this is the data encryption key
    data_encryption_key = get_random_bytes(16)
    print("1 {}".format(data_encryption_key))

    # Encrypt the data encryption key with the padded public key
    cipher_rsa = PKCS1_OAEP.new(key)
    encrypted_data_encrypted_key = cipher_rsa.encrypt(data_encryption_key)

    # AES Encrypt the data with the data encryption key
    cipher_aes = AES.new(data_encryption_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(data.encode("utf-8"))

    print('your encrypted text is : {}'.format(ciphertext))
    print('the tag is : {}'.format(tag))

    # pad the private key
    reconstructed_private_key = RSA.importKey(private_key)
    padded_private_key = PKCS1_OAEP.new(reconstructed_private_key)

    # decrypt the data encryption key bytes with the private key
    reconstructed_data_encryption_key_bytes = padded_private_key.decrypt(encrypted_data_encrypted_key)
    print("2 {}".format(reconstructed_data_encryption_key_bytes))

    # use bytes from previous step to recreate cipher, don't forget the nonce
    reconstructed_data_encryption_key = AES.new(reconstructed_data_encryption_key_bytes, AES.MODE_EAX, cipher_aes.nonce)

    # decrypt the text with the data encryption key
    decrypted_text = reconstructed_data_encryption_key.decrypt_and_verify(ciphertext, tag)
    # reconstructed_data_encryption_key.verify(tag)
    print('3 {}'.format(decrypted_text.decode("utf-8")))


def create_sqlite_db():
    if not os.path.isfile("crypto.db"):
        connection = sqlite3.connect("crypto.db")
        cursor = connection.cursor()
        try:
            cursor.execute('''CREATE TABLE user (id TEXT PRIMARY KEY, public_key BLOB, private_key BLOB)''')
        finally:
            connection.close()


def create_user():
    # returns user_id

    insert_user_sql = "INSERT INTO user (id, public_key, private_key) VALUES (?, ?, ?)"

    user_id = str(uuid.uuid4())

    key = RSA.generate(1024)
    private_key = key.export_key('PEM')
    public_key = key.publickey().exportKey('PEM')

    connection = sqlite3.connect("crypto.db")
    try:
        cursor = connection.cursor()
        cursor.execute(insert_user_sql, [user_id, public_key, private_key])
        connection.commit()
    finally:
        connection.close()

    return user_id


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
            "id": users[0][0],
            "publicKey": users[0][1],
            "privateKey": users[0][2]
        }

    return user


def encrypt_message_for_user(user_id, message):
    user = get_user(user_id)

    public_key = RSA.importKey(user["publicKey"])
    padded_public_key = PKCS1_OAEP.new(public_key)
    data_encryption_key = get_random_bytes(16)
    encrypted_data_encryption_key = padded_public_key.encrypt(data_encryption_key)

    cipher = AES.new(data_encryption_key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(message.encode("utf-8"))

    return ciphertext, encrypted_data_encryption_key,tag, cipher.nonce


def decrypt_message_for_user(user_id, encrypted_data_encryption_key, ciphertext, tag, nonce):
    user = get_user(user_id)

    private_key = RSA.importKey(user["privateKey"])
    padded_private_key = PKCS1_OAEP.new(private_key)

    data_encryption_key = padded_private_key.decrypt(encrypted_data_encryption_key)

    cipher = AES.new(data_encryption_key, AES.MODE_EAX, nonce)

    message = cipher.decrypt_and_verify(ciphertext, tag)

    return message.decode("utf-8")


if __name__ == "__main__":
    ciphertext, encrypted_data_encryption_key, tag, nonce = encrypt_message_for_user("1ffe3512-1def-4e1d-ae24-6a3ac31c6ff0", "Here fishy fishy fishy!")
    message = decrypt_message_for_user("1ffe3512-1def-4e1d-ae24-6a3ac31c6ff0",  encrypted_data_encryption_key, ciphertext, tag, nonce)
    print(message)
