from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import config

db = SQLAlchemy()
migration = Migrate()
csrf = CSRFProtect()

def create_app(config_name) -> Flask:
    """Creates a Flask application Instance."""
    app = Flask(__name__)

    # apply configuration
    app.config.from_object(config[config_name])

    # initialize extensions: order matters
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # import and register two blueprints: main and admin.users
    from app.routes.admin.users import bp as admin_users_blueprint
    app.register_blueprint(admin_users_blueprint, url_prefix='/admin/users')

    from app.routes.main import bp as main
    app.register_blueprint(main_blueprint)

    return app
