import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret")
    JWT_SECRET = os.getenv("JWT_SECRET", "dev_jwt_secret")

    NOTION_TOKEN = os.getenv("NOTION_TOKEN")
    NOTION_USERS_DB_ID = os.getenv("NOTION_USERS_DB_ID")
    NOTION_ENROLLMENTS_DB_ID = os.getenv("NOTION_ENROLLMENTS_DB_ID")
    NOTION_CHALLENGES_DB_ID = os.getenv("NOTION_CHALLENGES_DB_ID")
    NOTION_DAILY_LOGS_DB_ID = os.getenv("NOTION_DAILY_LOGS_DB_ID")

    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME")

    # Cookie auth
    JWT_COOKIE_NAME = os.getenv("JWT_COOKIE_NAME", "ringo_token")
    JWT_COOKIE_SECURE = os.getenv("JWT_COOKIE_SECURE", "0") == "1"
    JWT_COOKIE_SAMESITE = os.getenv("JWT_COOKIE_SAMESITE", "Lax")

