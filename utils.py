import sys
import time
import random
import dbutils
import passutils
from slowtype import slow_type

#mainfile
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
            connection = dbutils.connect_to_db(dbutils.DB_FILENAME)
            dbutils.create_table(connection)
            if action == 1:
                entry = dbutils.create_entry()
                if dbutils.commit_entry_to_db(connection,entry):
                    slow_type("\nEntry successfully added.\n")
            elif action == 2:
                dbutils.get_entry_from_db(connection)
            elif action == 3:
                dbutils.delete_entry_from_db(connection)
            elif action == 4:
                dbutils.display_all_entries(connection)
        elif action == 5:
            slow_type("\nExiting...\n")
            sys.exit()
        else:
            slow_type("Invalid Action.\n")

#mainfile
def main():
    attempts = 0
    while attempts < 3:
        if passutils.password_check(passutils.get_password()):
            slow_type("Access Granted.\n")
            actions()
        else:
            slow_type("Access Denied.\n")
            attempts += 1
            if attempts > 0:
                slow_type("{} more attempt(s) left.\n".format(passutils.MAX_ATTEMPTS - attempts))
    slow_type("Maximum attempts reached.\nExiting...\n")
    sys.exit()