from flask import request, jsonify
from functools import wraps
import jwt
from datetime import datetime, timedelta, timezone
from database import get_user_by_username, verify_password, get_user_by_id, create_user, get_user_by_telegram_id
import os

JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-this")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24 * 7  # 7 days

def make_jwt(payload: dict):
    """Create JWT token"""
    exp = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = dict(payload)
    payload["exp"] = int(exp.timestamp())
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_jwt(token: str):
    """Verify JWT token and return claims"""
    try:
        claims = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return claims
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_auth(optional=False):
    """
    Decorator to require authentication.
    Returns claims dict if authenticated, or aborts with 401 if not (unless optional=True)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = None

            # 1) Try Cookie first (HttpOnly)
            cookie_name = os.getenv("JWT_COOKIE_NAME", "ringo_token")
            token = request.cookies.get(cookie_name)

            # 2) Fallback to Authorization header Bearer
            if not token:
                auth = request.headers.get("Authorization", "")
                if auth.lower().startswith("bearer "):
                    token = auth.split(" ", 1)[1].strip()

            if not token:
                if optional:
                    return f(None, *args, **kwargs)
                return jsonify({"ok": False, "error": "unauthorized"}), 401

            claims = verify_jwt(token)
            if not claims:
                if optional:
                    return f(None, *args, **kwargs)
                return jsonify({"ok": False, "error": "invalid_token"}), 401

            return f(claims, *args, **kwargs)
        return decorated_function
    return decorator

def set_auth_cookie(resp, token: str):
    """Set authentication cookie"""
    cookie_name = os.getenv("JWT_COOKIE_NAME", "ringo_token")
    secure = os.getenv("JWT_COOKIE_SECURE", "0") == "1"
    samesite = os.getenv("JWT_COOKIE_SAMESITE", "Lax")

    resp.set_cookie(
        cookie_name,
        token,
        httponly=True,
        secure=secure,
        samesite=samesite,
        max_age=JWT_EXPIRATION_HOURS * 3600,
        path="/",
    )
    return resp

def get_token_from_request():
    """Extract token from request (cookie or header)"""
    cookie_name = os.getenv("JWT_COOKIE_NAME", "ringo_token")
    token = request.cookies.get(cookie_name)

    if not token:
        auth = request.headers.get("Authorization", "")
        if auth.lower().startswith("bearer "):
            token = auth.split(" ", 1)[1].strip()

    return token

# ==================== AUTH ROUTES ====================

def register_auth_routes(app):
    """Register all auth routes to Flask app"""
    
    @app.post("/auth/register")
    def register():
        """Register new user with username and password"""
        data = request.get_json(silent=True) or {}
        
        username = (data.get("username") or "").strip()
        password = (data.get("password") or "").strip()
        name = (data.get("name") or "").strip()
        email = (data.get("email") or "").strip()
        
        # Validation
        if not username or len(username) < 3:
            return jsonify({"ok": False, "error": "username_min_3_chars"}), 400
        
        if not password or len(password) < 6:
            return jsonify({"ok": False, "error": "password_min_6_chars"}), 400
        
        if email and "@" not in email:
            return jsonify({"ok": False, "error": "invalid_email"}), 400
        
        try:
            user_id = create_user(
                username=username,
                password=password,
                name=name or username,
                email=email or None
            )
            
            claims = {
                "user_id": user_id,
                "username": username,
                "name": name or username,
                "auth_method": "local"
            }
            
            token = make_jwt(claims)
            
            resp = jsonify({
                "ok": True,
                "user_id": user_id,
                "username": username,
                "access_token": token
            })
            
            return set_auth_cookie(resp, token), 201
            
        except ValueError as e:
            return jsonify({"ok": False, "error": str(e)}), 409



    @app.post("/auth/login")
    def login():
        """Login with username and password"""
        data = request.get_json(silent=True) or {}
        
        username = (data.get("username") or "").strip()
        password = (data.get("password") or "").strip()
        
        if not username or not password:
            return jsonify({"ok": False, "error": "username_and_password_required"}), 400
        
        user = verify_password(username, password)
        
        if not user:
            return jsonify({"ok": False, "error": "invalid_credentials"}), 401
        
        claims = {
            "user_id": user["id"],
            "username": user["username"],
            "name": user["name"],
            "auth_method": "local"
        }
        
        token = make_jwt(claims)
        
        resp = jsonify({
            "ok": True,
            "user_id": user["id"],
            "username": user["username"],
            "access_token": token
        })
        
        return set_auth_cookie(resp, token), 200

    @app.post("/auth/logout")
    def logout():
        """Logout user"""
        from flask import make_response
        resp = make_response(jsonify({"ok": True}), 200)
        
        cookie_name = os.getenv("JWT_COOKIE_NAME", "ringo_token")
        secure = os.getenv("JWT_COOKIE_SECURE", "0") == "1"
        samesite = os.getenv("JWT_COOKIE_SAMESITE", "Lax")
        
        resp.set_cookie(
            cookie_name,
            "",
            max_age=0,
            expires=0,
            httponly=True,
            secure=secure,
            samesite=samesite,
            path="/",
        )
        return resp