from datetime import datetime
from flask import url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user

db = SQLAlchemy()


class Base(db.Model):
    __abstract__ = True
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime,
                           default=datetime.utcnow,
                           onupdate=datetime.utcnow)


class UserBase(Base, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, index=True, nullable=False)
    email = db.Column(db.String(64), unique=True, index=True, nullable=False)
    phone = db.Column(db.Integer, unique=True, index=True, nullable=False)
    _password = db.Column('password', db.String(128), nullable=False)
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

    ROLE_USER = 10
    ROLE_COMPANY = 20
    ROLE_ADMIN = 30

    role = db.Column(db.SmallInteger, default=ROLE_USER)
    resume = db.relationship('Resume', backref='user')

    def __repr__(self):
        return '<User: {}>'.format(self.username)

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN

    @property
    def is_user(self):
        return self.role == self.ROLE_SEEKER

    @property
    def is_company(self):
        return self.role == self.ROLE_COMPANY


class Company(UserBase):
    __tablename__ = 'company'

    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"))
    user = db.relationship("User", uselist=False, backref=db.backref("company_detail", uselist=False))
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

    id = db.Column(db.Integer, primary_key=True)
    job_name = db.Column(db.String(32), index=True)
    salary_min = db.Column(db.Integer, nullable=False)
    salary_max = db.Column(db.Integer, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    company = db.relationship('User', uselist=False, backref=db.backref('jobs', lazy='dynamic'))
    # 职位描述
    description = db.Column(db.Text)
    # 职位待遇
    treatment = db.Column(db.Text)
    # 经验要求
    exp = db.Column(db.String(64), nullable=False)
    # 学历要求
    education = db.Column(db.String(64), nullable=False)
    # 技术栈要求
    stacks = db.Column(db.String(128))
    # 工作地点
    location = db.Column(db.String(32))
    # 职位标签
    tags = db.Column(db.String(128))
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

    @property
    def current_user_is_applied(self):
        delivery = Delivery.query.filter_by(job_id=self.id, user_id=current_user.id).first()
        return delivery is not None


class Resume(Base):
    __tablename__ = 'resume'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    fullname = db.Column(db.String(64), nullable=False)
    phone = db.Column(db.Integer, unique=True, index=True, nullable=False)
    email = db.Column(db.String(64), unique=True, index=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    # 性别 True男 False女
    gender = db.Column(db.Boolean, default=True)
    # 学历
    education = db.Column(db.String(64), nullable=False)
    # 工作年数
    job_year = db.Column(db.Integer, nullable=False)
    # 求职地点
    location = db.Column(db.String(32))
    website = db.Column(db.String(64))
    # 简述
    profile = db.Column(db.String(256), nullable=False)
    # 工作经历
    job_history = db.Column(db.Text)
    # 项目经验
    project_exp = db.Column(db.Text)
    # 期望薪水
    expected_salary = db.Column(db.Integer, nullable=False)
    # 是否公开
    is_enable = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return '<Resume: {}'.format(self.title)


class Delivery(Base):
    __tablename__ = 'delivery'

    STATUS_WAITTING = 1
    STATUS_REJECT = 2
    STATUS_ACCEPT = 3

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id', ondelete='SET NULL'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'))
    company_id = db.Column(db.Integer)
    status = db.Column(db.SmallInteger, default=STATUS_WAITTING)
    company_response = db.Column(db.String(256))

    @property
    def user(self):
        return User.query.get(self.user_id)

    @property
    def job(self):
        return Job.query.get(self.job_id)
