import os


class BaseConfig(object):
    SECRET_KEY = 'makesure to set a very secret key'
    JOB_INDEX_PER_PAGE = 18
    COMPANY_INDEX_PER_PAGE = 20
    LIST_PER_PAGE = 20


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root@localhost:3306/job_web?charset=utf8'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOADED_PDF_ALLOW = ('pdf',)
    UPLOADED_PDF_DEST = os.path.join(os.getcwd(), 'static', 'resumes')
    UPLOADED_PDF_SIZE = 3 * 1024 * 1024


class ProductionConfig(BaseConfig):
    pass


class TestingConfig(BaseConfig):
    pass


configs = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}


