# add_test_user.py
from database import init_db, create_user

def main():
    # اول مطمئن می‌شیم جدول وجود داره
    init_db()

    # اینجا یوزر تست را می‌سازیم
    username = "admin"
    password = "admin123"   # بعداً حتماً تغییر بده
    name = "Admin User"

    create_user(username, password, name)
    print(f"User created (or already existed): {username}")

if __name__ == "__main__":
    main()
