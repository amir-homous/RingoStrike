import sqlite3
import os

#for test
#this Pythone Code is for check database users
DB_NAME = "users.db"

def read_db():
    db_path = os.path.abspath(DB_NAME)
    print("DB path:", db_path)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print("Tables:", cursor.fetchall())

    cursor.execute("SELECT * FROM users")
    print("Users:", cursor.fetchall())

    conn.close()

if __name__ == "__main__":
    read_db()
