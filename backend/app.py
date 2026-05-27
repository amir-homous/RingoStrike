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

load_dotenv()


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)


    CORS(app, supports_credentials=True, resources={
        r"/*": {
            "origins": [
                "http://localhost:5173",
                "http://localhost:4173",
                "http://127.0.0.1:5173",
                "http://127.0.0.1:4173",
            ]
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


    # ✅ NOW YOUR OTHER ROUTES FOLLOW BELOW
    @app.get("/health")
    def health():
        return {"ok": True}
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)