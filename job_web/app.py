from flask import Flask
from jobplus.config import configs
from jobplus.models import db, User, Company
from flask_ckeditor import CKEditor
from flask_migrate import Migrate
from flask_moment import Moment
from flask_login import LoginManager
from flask_uploads import UploadSet, configure_uploads, patch_request_class

uploaded_pdf = UploadSet('pdf', ('pdf', ))


def register_extensions(app):
    db.init_app(app)
    Migrate(app, db)
    CKEditor(app)
    Moment(app)
    configure_uploads(app, uploaded_pdf)
    patch_request_class(app, app.config['UPLOADED_PDF_SIZE'])
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def user_loader(id):
        if User.query.get(id):
            return User.query.get(id)
        elif Company.query.get(id):
            return Company.query.get(id)

    login_manager.login_view = 'front.login'
    login_manager.login_message = '该页面需要登录后访问'


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
