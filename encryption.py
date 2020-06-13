import sys
import base64
from slowtype import slow_type
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.exceptions import InvalidSignature
from getpass import getpass 

KEY = None

#securefile
def encrypt_entry(*args):
    encrypted_entries = []
    generate_key()
    f = Fernet(KEY)
    for arg in args:
        encrypted_entries.append(f.encrypt(arg.encode()))
    return tuple(encrypted_entries)

#securefile
def generate_key_from_passkey(passkey):
    global KEY
    passkey_e = passkey.encode()
    salt = b'ipf_ergm_'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    KEY = base64.urlsafe_b64encode(kdf.derive(passkey_e))
    return KEY

#securefile
def decrypt_entry(*args):
    decrypted_entries = []
    generate_key()
    f = Fernet(KEY)
    for arg in args:
        try:
            darg = f.decrypt(arg)
            decrypted_entries.append(darg.decode("utf-8"))
        except InvalidToken as iserror:
            print(iserror)
            slow_type("Error: Incorrect passkey.\nExiting.......")
            sys.exit()
    return tuple(decrypted_entries)
    
#securefile
def generate_key():
    if not KEY:
        passkey = getpass(prompt="Enter Passkey: ")
        generate_key_from_passkey(passkey)