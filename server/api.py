import random, string, uuid
import pickle
import hashlib
import base64
import datetime, calendar
import logging

from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_v1_5, PKCS1_OAEP
from logging import getLogger

## Advanced Encryption Standard
## encrypt text with aes, generate iv and wrap altogether in json format with nonce from cipher
## nonce is going to be used when decrypt aes
## cipher generates nonce and encrypts message with iv

## [BEGIN] private apis 
## key == session key/symmetric key, discarded every time it finishes the execution
def _encrypt_aes(raw_txt):
    key = hashlib.sha256(get_random_bytes(AES.block_size)).digest() # => a 32 byte string
    padded_txt = _padding(raw_txt)
    iv = Random.new().read(AES.block_size)   ## iv == nonce
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return {'key': key, 'iv': iv, 'cipher_txt': base64.b64encode(cipher.encrypt(padded_txt))}  


# encrypt key(symmetric key) with receiver's public_key
def _encrypt_rsa(public_key, key):
    if type(public_key) is unicode:
        public_key = RSA.importKey(public_key)
    cipher_rsa = PKCS1_v1_5.new(public_key)
    return cipher_rsa.encrypt(key)


def _padding(txt):
    return txt+(AES.block_size-len(txt)%AES.block_size)*chr(AES.block_size-len(txt)%AES.block_size)


# decrypt text using key from aes algorithm
def _decrypt_aes(key, iv, cipher_txt):
    cipher_txt = base64.b64decode(cipher_txt)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    test =  cipher.decrypt(cipher_txt)
    return _unpadding(test.decode('utf-8'))


## Rivest, Shamir, Adleman
## decrypt iv encrypted by sender's public key to decrypt message content was encrypted with aes
def _decrypt_rsa(private_key, secured_key):
    if type(private_key) is unicode:
        private_key = RSA.importKey(private_key)
    cipher_rsa = PKCS1_v1_5.new(private_key)
    ## added for using PKCS1_v1_5, not needed when using PKCS1_OAEP
    dsize = SHA.digest_size
    sentinel = Random.new().read(16+dsize)              # Let's assume that average data length is 16
    ## ------------------
    return cipher_rsa.decrypt(secured_key, sentinel)


def _unpadding(txt):
    return txt[:-ord(txt[len(txt)-1:])]


## [BEGIN] public apis
## encrypt message between clients and web server
def encrypt_msg(public_key, message):
    aes_encrypted_data = _encrypt_aes(message)
    return pickle.dumps({'secured_data': pickle.dumps(aes_encrypted_data), 
        'secured_key':_encrypt_rsa(public_key, aes_encrypted_data['key'])})


def decrypt_msg(private_key, encrypted_msg):
    encrypted_msg = pickle.loads(encrypted_msg)
    secured_data = pickle.loads(encrypted_msg.pop('secured_data',[]))
    key = _decrypt_rsa(private_key, encrypted_msg.pop('secured_key',[]))
    return _decrypt_aes(key, 
        secured_data.pop('iv',[]), 
        secured_data.pop('cipher_txt',[]))


## generate public_key from private_key
## api for keys
def generate_public_key(private_key):
    print type(private_key)
    return private_key.publickey()


## Rivest, Shamir, Adleman
## RSA for generating keys
def generate_private_key():
    rand = Random.new().read
    return RSA.generate(1024, rand)

## [END] public apis

## [BEGIN] apis not allowed to override 
## generate uuid based on host id and current time
def __uuid_generator_1():
    return uuid.uuid1()


## generate random uuid
def __uuid_generator_4():
    return uuid.uuid4()


def __get_logger(logger_name):
    ## [BEGIN]logger settings 
    logger = getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter("%(asctime)s-%(name)s-%(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)
    ## [END]
    return logger


def __get_current_time():
    return datetime.datetime.now()

def __get_unix_from_datetime(dt):
    return calendar.timegm(dt.timetuple())

## [END] apis not allowed to override 