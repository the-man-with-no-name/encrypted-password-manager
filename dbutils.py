import sqlite3
from datetime import datetime
from sqlite3 import Error
from getpass import getpass
from encryption import encrypt_entry, decrypt_entry, generate_key
from slowtype import slow_type

DB_FILENAME = 'database/data.db'

#dbfile
def connect_to_db(db_file):
    connection = None
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as error:
        print(error)
    return connection

#dbfile
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

#dbfile
def create_entry():
    identifier = input("\nIdentifier for entry: ").strip()
    username = getpass(prompt="Username: ")
    password = getpass()
    last_update = datetime.now().strftime("%H:%M:%S;%m/%d/%Y")
    generate_key()
    entry = encrypt_entry(username,password,last_update)
    return (identifier,*entry)

#dbfile
def format_response(response):
    f_response = []
    for r in response:
        f_response.append(r[0])
    return f_response

#dbfile
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

#dbfile
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

#dbfile
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
                        newname = getpass("Enter new username: ").strip()
                        cursor.execute("""
                            UPDATE login 
                            SET username = ? 
                            WHERE identifier = ?;
                        """, (*encrypt_entry(newname), identifier))
                    else:
                        newpass = getpass("Enter new password: ").strip()
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

#dbfile
def display_entry(entry):
    decrypted_entry = decrypt_entry(entry[1],entry[2],entry[3])
    slow_type("\n\tIdentifier: {}".format(entry[0]))
    slow_type("\tUsername: {}".format(decrypted_entry[0]))
    slow_type("\tPassword: {}".format(decrypted_entry[1]))
    slow_type("\tLast Modified: {}\n".format(decrypted_entry[2]))

#dbfile
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

#dbfile
def delete_entry_from_db(connection):
    identifier = input("Enter the identifier of the entry you wish to delete: ").strip()
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