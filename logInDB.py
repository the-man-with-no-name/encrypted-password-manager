import sqlite3
import os 
import sys
import time
import random
import base64
from datetime import datetime
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.exceptions import InvalidSignature
from getpass import getpass 
from sqlite3 import Error

DB_FILENAME = None #.db FILENAME HERE
PASSWORD = None #PASSWORD HERE
KEY = None 
MAX_ATTEMPTS = 3 #MAX ALLOWED PASSWORD ATTEMPTS

def connect_to_db(db_file):
    connection = None
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as error:
        print(error)
    return connection

def create_table(connection):
    try:
        connection.execute("""
        CREATE TABLE IF NOT EXISTS login (
            identifier      TEXT,
            username        VARBINARY,
            password        VARBINARY,
            lastmodified    VARBINARY
        )
        """)
    except sqlite3.OperationalError as operror:
        print(operror)

def encrypt_entry(*args):
    encrypted_entries = []
    generate_key()
    f = Fernet(KEY)
    for arg in args:
        encrypted_entries.append(f.encrypt(arg.encode()))
    return tuple(encrypted_entries)

def create_entry():
    identifier = input("\nIdentifier for entry: ")
    username = getpass(prompt="Username: ")
    password = getpass()
    last_update = datetime.now().strftime("%H:%M:%S;%m/%d/%Y")
    generate_key()
    entry = encrypt_entry(username,password,last_update)
    return (identifier,*entry)

def format_response(response):
    f_response = []
    for r in response:
        f_response.append(r[0])
    return f_response

def commit_entry_to_db(connection,entry):
    try:
        with connection:
            cursor = connection.cursor()
            ids = None
            cursor.execute('SELECT identifier FROM login')
            ids = cursor.fetchall()
            if entry[0] not in format_response(ids):
                cursor.execute("""
                    INSERT INTO login(identifier,username,password,lastmodified)
                    VALUES(?,?,?,?)
                """,entry)
                return True
            else:
                slow_type("\nAn entry with the identifier {} already exists.".format(entry[0]))
                slow_type("Identifiers must be unique.\n")
                return False
    except sqlite3.OperationalError as operror:
        print(operror)
    return False

def get_entry_from_db(connection):
    identifier = input("Enter the identifier of the entry you wish to retrieve: ")
    entry = None
    try:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM login WHERE identifier = ?',(identifier,))
        entry = cursor.fetchall()
    except sqlite3.OperationalError as operror:
        print(operror)
    if entry:
        slow_type("...............\n",typing_speed=400,random_speed=False)
        slow_type("Entry Found:\n")
        display_entry(entry[0])
        while True:
            modify = input("Would you like to modify this entry? [Y/N] ")
            if modify == 'Y':
                change_entry(connection,identifier)
            elif modify == 'N':
                return
            else:
                print("Invalid response.\n")
    else:
        slow_type("...............\n",typing_speed=400,random_speed=False)
        slow_type("Entry Not Found.\n")

def change_entry(connection,identifier):
    while True:
        slow_type("\nWhat attribute(s) would you like to change?\n")
        slow_type("\t[1] Username")
        slow_type("\t[2] Password")
        slow_type("\t[3] No change\n")
        field_to_change = int(input("--> "))
        if field_to_change == 1 or field_to_change == 2:
            try:
                with connection:
                    cursor = connection.cursor()
                    if field_to_change == 1:
                        newname = getpass("Enter new username: ")
                        cursor.execute("""
                            UPDATE login 
                            SET username = ? 
                            WHERE identifier = ?;
                        """, (*encrypt_entry(newname), identifier))
                    else:
                        newpass = getpass("Enter new password: ")
                        cursor.execute("""
                            UPDATE login 
                            SET password = ? 
                            WHERE identifier = ?;
                        """, (*encrypt_entry(newpass), identifier))
                    last_update = datetime.now().strftime("%H:%M:%S;%m/%d/%Y")
                    cursor.execute("""
                        UPDATE login 
                        SET lastmodified = ? 
                        WHERE identifier = ?;
                    """, (*encrypt_entry(last_update), identifier))
            except sqlite3.OperationalError as operror:
                print(operror)
            slow_type("Entry successfully updated.\n")
        elif field_to_change == 3:
            return 
        else:
            slow_type("Invalid field. Please select [1], [2], or [3].")
    return

def display_entry(entry):
    decrypted_entry = decrypt_entry(entry[1],entry[2],entry[3])
    slow_type("\n\tIdentifier: {}".format(entry[0]))
    slow_type("\tUsername: {}".format(decrypted_entry[0]))
    slow_type("\tPassword: {}".format(decrypted_entry[1]))
    slow_type("\tLast Modified: {}\n".format(decrypted_entry[2]))

def display_all_entries(connection):
    try:
        with connection:
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM login')
            entries = cursor.fetchall()
            slow_type("\nFound {} entries in database.\n".format(len(entries)))
            for entry in entries:
                display_entry(entry)
    except sqlite3.OperationalError as operror:
        print(operror)

def delete_entry_from_db(connection):
    identifier = input("Enter the identifier of the entry you wish to delete: ")
    try:
        with connection:
            en = None
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM login WHERE identifier = ?',(identifier,))
            en = cursor.fetchall()
            if en:
                slow_type("\nEntry Found.\n")
                display_entry(en[0])
                while True:
                    delete = input('Are you sure you wish to delete this entry? [Y/N] ')
                    if delete == 'Y':
                        slow_type("\nDeleting entry........\n")
                        cursor.execute("DELETE FROM login WHERE identifier = ?",(identifier,))
                        slow_type("Entry successfully deleted.\n")
                        return
                    elif delete == 'N':
                        return
                    else:
                        slow_type("Invalid response. Select Y or N.\n")
            else:
                slow_type("\nNo entry found with identifier: {}\n".format(identifier))
    except sqlite3.OperationalError as operror:
        print(operror)
    return 

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
    
def generate_key():
    if not KEY:
        passkey = getpass(prompt="Enter Passkey: ")
        generate_key_from_passkey(passkey)

def password_check(password):
    if password == PASSWORD:
        return True
    return False

def slow_type(t,typing_speed=500,random_speed=True):
    for l in t:
        sys.stdout.write(l)
        sys.stdout.flush()
        if random_speed:
            time.sleep(random.random()*10.0/typing_speed)
        else:
            time.sleep(10.0/typing_speed)
    print('')

def get_password():
    password = getpass()
    slow_type("...............\n",typing_speed=400,random_speed=False)
    return password

def actions():
    while True:
        slow_type("\nChoose Action:\n")
        slow_type("\t[1] Create new entry.")
        slow_type("\t[2] Retrieve entry.")
        slow_type("\t[3] Delete entry.")
        slow_type("\t[4] Display all entries.")
        slow_type("\t[5] Exit.\n")
        action = int(input("--> "))
        if action in [1,2,3,4]:
            # actionable actions
            connection = connect_to_db(DB_FILENAME)
            create_table(connection)
            if action == 1:
                entry = create_entry()
                if commit_entry_to_db(connection,entry):
                    slow_type("\nEntry successfully added.\n")
            elif action == 2:
                get_entry_from_db(connection)
            elif action == 3:
                delete_entry_from_db(connection)
            elif action == 4:
                display_all_entries(connection)
        elif action == 5:
            slow_type("\nExiting...\n")
            sys.exit()
        else:
            slow_type("Invalid Action.\n")

def main():
    attempts = 0
    while attempts < 3:
        if password_check(get_password()):
            slow_type("Access Granted.\n")
            actions()
        else:
            slow_type("Access Denied.\n")
            attempts += 1
            if attempts > 0:
                slow_type("{} more attempt(s) left.\n".format(MAX_ATTEMPTS - attempts))
    slow_type("Maximum attempts reached.\nExiting...\n")
    sys.exit()

if __name__ == '__main__':
    main()