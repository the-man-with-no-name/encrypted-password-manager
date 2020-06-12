# encrypted-password-manager
Password manager of encrypted log-in information stored in .db file.
To run, type ```python logInDB.py```
This file requires the following packages:
```sqlite3``` ```cryptography``` ```getpass```.

WARNING: To use this file, you must use a passkey for the encryption. This key is not stored within the python file nor the database. You must remember this passkey to encrypt and decrypt the data in the .db file. If you forget this passkey, you will not be able to decrypt the data.
