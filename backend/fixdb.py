import sqlite3

def upgrade_db():
    conn = sqlite3.connect('users.db') # مطمئن شو مسیر فایل درست است
    cursor = conn.cursor()
    
    # اضافه کردن ستون‌های غایب
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN total_points INTEGER DEFAULT 0")
        print("Added: total_points")
    except sqlite3.OperationalError:
        print("Column already exists: total_points")

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN current_streak INTEGER DEFAULT 0")
        print("Added: current_streak")
    except sqlite3.OperationalError:
        print("Column already exists: current_streak")

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN longest_streak INTEGER DEFAULT 0")
        print("Added: longest_streak")
    except sqlite3.OperationalError:
        print("Column already exists: longest_streak")

    conn.commit()
    conn.close()
    print("Database upgraded successfully!")

if __name__ == "__main__":
    upgrade_db()
