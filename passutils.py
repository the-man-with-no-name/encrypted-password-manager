import hashlib
from getpass import getpass
from slowtype import slow_type

PS_FILENAME = 'data/pass.txt'
MAX_ATTEMPTS = 3

#passfile
def change_password():
    return

#passfile
def secure_password(password):
    dk = hashlib.pbkdf2_hmac('sha256', password.encode(), password[0:len(password)//2].encode(), 100000)
    return dk.hex()

#passfile
def retrieve_password():
    f = open(PS_FILENAME, 'r')
    password = None
    try:
        password = f.read()
    finally:
        f.close()
    return password

#passfile
def password_check(password):
    if secure_password(password) == retrieve_password():
        return True
    return False

#passfile
def get_password():
    password = getpass()
    slow_type("...............\n",typing_speed=400,random_speed=False)
    return password