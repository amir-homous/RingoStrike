import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from config import Config
from database import init_db
from routes.auth_routes import register_auth_blueprint
from routes.challenge_routes import challenge_bp
from routes.dashboard_routes import dashboard_bp
from routes.enrollment_routes import enrollment_bp
from routes.leaderboard_routes import leaderboard_bp
from routes.history_routes import history_bp
from routes.debug_routes import debug_bp
from routes.stats_routes import stats_bp
from routes.public_profile_routes import public_profile_bp
from routes.profile_settings_routes import profile_settings_bp
from routes.health_routes import health_bp
from routes.telegram_routes import telegram_bp
from routes.path_routes import path_bp
from routes.mission_routes import mission_bp


load_dotenv()

def get_cors_origins() -> list[str]:
    default_origins = [
        "http://localhost:5173",
        "http://localhost:4173",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:4173",
    ]

    env_origins = []

    for key in (
        "CORS_ORIGINS",
        "FRONTEND_ORIGIN",
        "FRONTEND_BASE_URL",
    ):
        value = os.getenv(key, "")
        if value:
            env_origins.extend(
                origin.strip()
                for origin in value.split(",")
                if origin.strip()
            )

    origins = [
        *default_origins,
        *env_origins,
    ]

    return list(dict.fromkeys(origins))


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)


    CORS(app, supports_credentials=True, resources={
        r"/*": {
            "origins": get_cors_origins()
        }
    })

    init_db()
    register_auth_blueprint(app)

    app.register_blueprint(challenge_bp)    
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(enrollment_bp)
    app.register_blueprint(leaderboard_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(debug_bp)
    app.register_blueprint(stats_bp)
    app.register_blueprint(public_profile_bp)
    app.register_blueprint(profile_settings_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(telegram_bp)
    app.register_blueprint(path_bp)
    app.register_blueprint(mission_bp)


    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)
