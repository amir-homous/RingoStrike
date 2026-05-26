import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "your-fallback-secret-key")
    JWT_SECRET = os.getenv("JWT_SECRET", "dev_jwt_secret")

    NOTION_TOKEN = os.getenv("NOTION_TOKEN")
    NOTION_USERS_DB_ID = os.getenv("NOTION_USERS_DB_ID")
    NOTION_ENROLLMENTS_DB_ID = os.getenv("NOTION_ENROLLMENTS_DB_ID")
    NOTION_CHALLENGES_DB_ID = os.getenv("NOTION_CHALLENGES_DB_ID")
    NOTION_DAILY_LOGS_DB_ID = os.getenv("NOTION_DAILY_LOGS_DB_ID")

    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME")

    # Cookie auth
    JWT_COOKIE_NAME = "ringo_token"
    JWT_COOKIE_SECURE = False
    JWT_COOKIE_SAMESITE = "Lax"

    
    # --- Local fallback auth (non-Telegram) ---
    LOCAL_LOGIN_ENABLED = os.getenv("LOCAL_LOGIN_ENABLED", "True").lower() == "True"
    
    # A shared secret code for fallback login (set in .env)
    # IMPORTANT: change this in production
    LOCAL_LOGIN_SECRET = os.getenv("LOCAL_LOGIN_SECRET", "supersecret123").strip()
    
    # If you want to force only telegram / only local / both
    AUTH_MODE = "all"
    # allowed: "telegram", "local", "both"

    DEMO_USER_ID = "12345"      # برای تست سریع