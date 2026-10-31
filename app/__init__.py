import os

from flask import Flask

from config import configs


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get("FLASK_CONFIG", "development")

    app = Flask(__name__)
    app.config.from_object(configs[config_name])

    if config_name == "production" and not os.environ.get("SECRET_KEY"):
        raise RuntimeError("SECRET_KEY must be set in production")

    from .routes import bp
    app.register_blueprint(bp)

    return app