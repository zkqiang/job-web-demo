from flask import Flask
from jobplus.config import configs
from jobplus.models import db, User
from flask_migrate import Migrate
from flask_login import LoginManager

def register_extensions(app):
    db.init_app(app)
    Migrate(app, db)
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def user_loader(id):
        return User.query.get(id)

    login_manager.login_view = 'front.login'

def register_blueprints(app):
    from .handlers import front, admin, user, company, resume, job
    app.register_blueprint(front)
    app.register_blueprint(user)
    app.register_blueprint(admin)
    app.register_blueprint(company)
    app.register_blueprint(resume)
    app.register_blueprint(job)

def create_app(config):
    app = Flask(__name__)
    app.config.from_object(configs.get(config))
    register_extensions(app)
    register_blueprints(app)
    db.init_app(app)
    return app
