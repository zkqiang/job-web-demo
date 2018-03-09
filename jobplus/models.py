from datetime import datetime
from flask import url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user

db = SQLAlchemy()


class Base(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime,
                           default=datetime.utcnow,
                           onupdate=datetime.utcnow)


class UserBase(Base, UserMixin):
    __tablename__ = 'user_base'

    username = db.Column(db.String(32), unique=True, index=True, nullable=False)
    email = db.Column(db.String(64), unique=True, index=True, nullable=False)
    phone = db.Column(db.Integer, unique=True, index=True, nullable=False)
    _password = db.Column('password', db.String(128), nullable=False)
    role = db.Column(db.SmallInteger, default=0)
    is_enable = db.Column(db.Boolean, default=True)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, orig_password):
        self._password = generate_password_hash(orig_password)

    def check_password(self, password):
        return check_password_hash(self._password, password)


class User(UserBase):
    __tablename__ = 'user'

    resume = db.Column(db.String(128))

    def __repr__(self):
        return '<User: {}>'.format(self.username)


class Company(UserBase):
    __tablename__ = 'company'

    website = db.Column(db.String(64))
    address = db.Column(db.String(256))
    logo = db.Column(db.String(256))
    # 融资进度
    finance_stage = db.Column(db.String(128))
    # 公司领域
    field = db.Column(db.String(64))
    # 简介
    profile = db.Column(db.String(1024))
    # 详情
    detail = db.Column(db.Text)

    def __repr__(self):
        return '<Company: {}'.format(self.username)


class Job(Base):
    __tablename__ = 'job'

    job_name = db.Column(db.String(32), index=True)
    salary_min = db.Column(db.Integer, nullable=False)
    salary_max = db.Column(db.Integer, nullable=False)
    # company_id = db.Column(db.Integer, db.ForeignKey('company.id', ondelete='CASCADE'))
    # company = db.relationship('Company', uselist=False, backref=db.backref('jobs', lazy='dynamic'))
    # 职位描述
    description = db.Column(db.Text)
    # 职位待遇
    treatment = db.Column(db.Text)
    # 经验要求
    exp = db.Column(db.String(16), nullable=False)
    # 学历要求
    education = db.Column(db.String(16), nullable=False)
    # 技术栈要求
    stacks = db.Column(db.String(128))
    # 工作地点
    location = db.Column(db.String(32))
    # 职位标签
    tags = db.Column(db.String(64))
    # 职位上线
    is_enable = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return '<Job: {}'.format(self.job_name)

    @property
    def url(self):
        return url_for('job.detail', course_id=self.id)

    @property
    def stack_list(self):
        return self.stacks.split(",")

    @property
    def tag_list(self):
        return self.tags.split(",")

    # @property
    # def current_user_is_applied(self):
    #     delivery = Delivery.query.filter_by(job_id=self.id, user_id=current_user.id).first()
    #     return delivery is not None


# class Delivery(Base):
#     __tablename__ = 'delivery'
#
#     STATUS_WAITTING = 1
#     STATUS_REJECT = 2
#     STATUS_ACCEPT = 3
#
#     job_id = db.Column(db.Integer, db.ForeignKey('job.id', ondelete='SET NULL'))
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'))
#     company_id = db.Column(db.Integer)
#     status = db.Column(db.SmallInteger, default=STATUS_WAITTING)
#     company_response = db.Column(db.String(256))
#
#     @property
#     def user(self):
#         return User.query.get(self.user_id)
#
#     @property
#     def job(self):
#         return Job.query.get(self.job_id)
#
#     def __repr__(self):
#         return '<Delivery: {}'.format(self.title)
