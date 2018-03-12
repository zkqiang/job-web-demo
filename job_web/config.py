import os
from flask_uploads import IMAGES


class BaseConfig(object):
    SECRET_KEY = 'makesure to set a very secret key'
    JOB_INDEX_PER_PAGE = 18
    COMPANY_INDEX_PER_PAGE = 20
    LIST_PER_PAGE = 20


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root@localhost:3306/job_web?charset=utf8'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOADED_PDF_ALLOW = IMAGES
    UPLOADED_PDF_DEST = os.path.join(os.getcwd(), 'static', 'resume')
    UPLOADED_PDF_SIZE = 512 * 1024
    UPLOADED_LOGO_ALLOW = IMAGES
    UPLOADED_LOGO_DEST = os.path.join(os.getcwd(), 'static', 'logo')
    UPLOADED_LOGO_SIZE = 50 * 1024


class ProductionConfig(BaseConfig):
    pass


class TestingConfig(BaseConfig):
    pass


configs = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}


