import os
from flask_uploads import IMAGES


class BaseConfig(object):
    SECRET_KEY = 'makesure to set a very secret key'
    JOB_INDEX_PER_PAGE = 18
    COMPANY_INDEX_PER_PAGE = 20
    COMPANY_DETAIL_PER_PAGE = 10
    LIST_PER_PAGE = 15


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root:123456@localhost:3306/job_web?charset=utf8'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOADED_SIZE = 300 * 1024
    UPLOADED_RESUME_ALLOW = IMAGES
    UPLOADED_RESUME_DEST = os.path.join(os.getcwd(), 'static', 'resume')
    UPLOADED_LOGO_ALLOW = IMAGES
    UPLOADED_LOGO_DEST = os.path.join(os.getcwd(), 'static', 'logo')


class ProductionConfig(BaseConfig):
    pass


class TestingConfig(BaseConfig):
    pass


configs = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}


