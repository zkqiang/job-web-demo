from datetime import datetime
from flask import url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user
from sqlalchemy import event, DDL

db = SQLAlchemy()


FINANCE_STAGE = ['未融资', '天使轮', 'A轮', 'B轮', 'C轮', 'D轮及以上', '上市公司', '不需要融资']
FIELD = ['移动互联网', '电子商务', '金融', '企业服务', '教育', '文化娱乐', '游戏', 'O2O', '硬件']
EXP = ['不限', '1年', '1-3年', '3-5年', '5-10年', '10年以上']
EDUCATION = ['不限学历', '专科', '本科', '硕士', '博士']
DEFAULT_LOGO = 'https://www.zhipin.com/v2/chat_v2/images/v2/defaultlogov2.jpg'


class Base(db.Model):
    __abstract__ = True

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime,
                           default=datetime.now,
                           onupdate=datetime.now)

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.name)


class UserBase(Base, UserMixin):
    __abstract__ = True

    ROLE_USER = 10
    ROLE_COMPANY = 20
    ROLE_ADMIN = 30

    email = db.Column(db.String(64), unique=True, nullable=False)
    # phone = db.Column(db.Integer, unique=True, index=True, nullable=False)
    _password = db.Column('password', db.String(128), nullable=False)
    is_enable = db.Column(db.Boolean, default=True, index=True)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, orig_password):
        self._password = generate_password_hash(orig_password)

    def is_user(self):
        return self.role == self.ROLE_USER

    def is_company(self):
        return self.role == self.ROLE_COMPANY

    def is_admin(self):
        return self.role == self.ROLE_ADMIN

    def check_password(self, password):
        return check_password_hash(self._password, password)


class User(UserBase):
    __tablename__ = 'user'

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(8), nullable=False)
    resume = db.Column(db.String(128))
    role = db.Column(db.SmallInteger, default=UserBase.ROLE_USER)


event.listen(User.__table__, "after_create", DDL("ALTER TABLE user AUTO_INCREMENT = 100000000"))


class Company(UserBase):
    __tablename__ = 'company'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, nullable=False)
    website = db.Column(db.String(256))
    address = db.Column(db.String(64))
    logo = db.Column(db.String(128), default=DEFAULT_LOGO)
    role = db.Column(db.SmallInteger, default=UserBase.ROLE_COMPANY)
    # 融资进度
    finance_stage = db.Column(db.String(16))
    # 公司领域
    field = db.Column(db.String(16))
    # 简介
    description = db.Column(db.String(256))
    # 详情
    details = db.Column(db.Text)

    def enabled_jobs(self):
        return self.jobs.filter(Job.is_enable.is_(True))


class Job(Base):
    __tablename__ = 'job'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    salary_min = db.Column(db.SmallInteger, nullable=False, index=True)
    salary_max = db.Column(db.SmallInteger, nullable=False, index=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id', ondelete='CASCADE'))
    company = db.relationship('Company', uselist=False, backref=db.backref('jobs', lazy='dynamic'))
    # 职位描述
    description = db.Column(db.Text)
    # 职位待遇
    treatment = db.Column(db.Text)
    # 经验要求
    exp = db.Column(db.String(16), default=EXP[0], index=True)
    # 学历要求
    education = db.Column(db.String(16), default=EDUCATION[0], index=True)
    # 工作城市
    city = db.Column(db.String(8), index=True)
    # 职位标签
    tags = db.Column(db.String(64))
    # 职位上线
    is_enable = db.Column(db.Boolean, default=True, index=True)

    @property
    def url(self):
        return url_for('job.detail', course_id=self.id)

    @property
    def tag_list(self):
        if self.tags and '，' in self.tags:
            return self.tags.split('，')
        return self.tags.split(',')

    def is_applied(self):
        delivery = current_user.delivery.filter_by(job_id=self.id).first()
        return delivery is not None


class Delivery(Base):
    __tablename__ = 'delivery'

    STATUS_WAITTING = 1
    STATUS_REJECT = 2
    STATUS_ACCEPT = 3

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id', ondelete='SET NULL'))
    job = db.relationship('Job', uselist=False, backref=db.backref('delivery', lazy='dynamic'))
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id', ondelete='SET NULL'))
    user = db.relationship('User', uselist=False, backref=db.backref('delivery', lazy='dynamic'))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id', ondelete='SET NULL'))
    company = db.relationship('Company', uselist=False, backref=db.backref('delivery', lazy='dynamic'))
    resume = db.Column(db.String(128))
    status = db.Column(db.SmallInteger, default=STATUS_WAITTING, index=True)
    company_response = db.Column(db.String(256))

    def accept(self):
        self.status = self.STATUS_ACCEPT

    def reject(self):
        self.status = self.STATUS_REJECT
