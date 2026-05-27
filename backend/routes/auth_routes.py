from auth import register_auth_routes

def register_auth_blueprint(app):
    # keeps existing auth endpoints/behavior untouched
    register_auth_routes(app)