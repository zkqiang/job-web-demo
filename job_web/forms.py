from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from flask_login import current_user
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import IntegerField, PasswordField, SelectField, \
    StringField, SubmitField, TextAreaField, ValidationError, BooleanField
from wtforms.validators import Email, EqualTo, Regexp, Length, URL, DataRequired
from .models import User, Company, db, Job, FINANCE_STAGE, FIELD, EDUCATION, EXP
from .app import uploaded_resume, uploaded_logo
import time
import random
import hmac


class RegisterUserForm(FlaskForm):

    email = StringField('邮箱', validators=[DataRequired(message='请填写内容'),
                                          Email(message='请输入合法的email地址')])
    password = PasswordField('密码', validators=[DataRequired(message='请填写密码'),
                                               Length(6, 24, message='须在6～24个字符之间'),
                                               Regexp(r'^[a-zA-Z]+\w+', message='仅限使用英文、数字、下划线，并以英文开头')])
    repeat_password = PasswordField('重复密码', validators=[DataRequired(message='请填写密码'),
                                                        EqualTo('password', message='两次密码不一致')])
    name = StringField('姓名', validators=[DataRequired(message='请填写内容'),
                                         Length(2, 8, message='须在2～8个字符之间')])
    submit = SubmitField('提交')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() or \
                Company.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被其他账号使用')

    def create_user(self):
        user = User()
        user.name = self.name.data
        user.email = self.email.data
        user.password = self.password.data
        user.id = int(time.time() * 100000000)
        db.session.add(user)
        db.session.commit()
        return user


class RegisterCompanyForm(FlaskForm):

    email = StringField('邮箱', validators=[DataRequired(message='请填写内容'),
                                          Email(message='请输入合法的Email地址')])
    password = PasswordField('密码', validators=[DataRequired(message='请填写密码'),
                                               Length(6, 24, message='须在6～24个字符之间'),
                                               Regexp(r'^[a-zA-Z]+\w+', message='仅限使用英文、数字、下划线，并以英文开头')])
    repeat_password = PasswordField('重复密码', validators=[DataRequired(message='请填写密码'),
                                                        EqualTo('password', message='两次密码不一致')])
    name = StringField('企业名称', validators=[DataRequired(message='请填写内容'),
                                           Length(2, 32, message='须在2～32个字符之间')])
    finance_stage = SelectField('融资阶段', choices=[(i, i) for i in FINANCE_STAGE])
    field = SelectField('行业领域', choices=[(i, i) for i in FIELD])
    description = StringField('公司简介', validators=[Length(0, 50, message='最多50个字符')])
    submit = SubmitField('提交')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() or \
                Company.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被其他账号使用')

    def create_company(self):
        company = Company()
        company.name = self.name.data
        company.email = self.email.data
        company.password = self.password.data
        db.session.add(company)
        db.session.commit()
        return company


class LoginForm(FlaskForm):

    email = StringField('邮箱', validators=[DataRequired(message='请填写内容'),
                                          Email(message='请输入合法的email地址')])
    password = PasswordField('密码', validators=[DataRequired(message='请填写密码'),
                                               Length(6, 24, message='须在6～24个字符之间')])
    remember_me = BooleanField('记住登录状态')
    submit = SubmitField('登录')


class UserDetailForm(RegisterUserForm):

    def validate_email(self, field):
        if current_user.email != self.email.data and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被其他账号使用')

    def update_detail(self, user):
        user.name = self.name.data
        user.email = self.email.data
        user.password = self.password.data
        db.session.add(user)
        db.session.commit()
        return user


class UserResumeForm(FlaskForm):

    resume = FileField('简历上传（暂仅支持图片，300KB以内）', validators=[
                FileAllowed(uploaded_resume, '不符合文件格式'),
                FileRequired('文件未选择')])
    submit = SubmitField('上传')

    def upload_resume(self, user):
        filename = uploaded_resume.save(self.resume.data, name=random_name())
        resume_url = uploaded_resume.url(filename)
        user.resume = resume_url
        db.session.add(user)
        db.session.commit()
        return resume_url


class CompanyDetailForm(FlaskForm):

    address = StringField('办公地址', validators=[Length(0, 128, message='最多128个字符')])
    logo = FileField('LOGO 上传（300KB以内）', validators=[
        FileAllowed(uploaded_logo, '不符合图片格式或大小')])
    finance_stage = SelectField('融资阶段', choices=[(i, i) for i in FINANCE_STAGE])
    field = SelectField('行业领域', choices=[(i, i) for i in FIELD])
    website = StringField('企业网址', validators=[URL(message='请输入正确网址')])
    description = TextAreaField('企业简介', validators=[Length(0, 50, message='最多50个字符')])
    details = CKEditorField('企业详情', validators=[Length(0, 1000, message='最多1000个字符')])
    submit = SubmitField('提交')

    def update_detail(self, company):
        self.populate_obj(company)
        filename = uploaded_logo.save(self.logo.data, name=random_name())
        logo_url = uploaded_logo.url(filename)
        company.logo = logo_url
        db.session.add(company)
        db.session.commit()
        return logo_url


class JobForm(FlaskForm):

    name = StringField('职位名称', validators=[DataRequired(message='请填写内容'), Length(4, 64)])
    salary_min = IntegerField('最低薪水（单位：千元）', validators=[DataRequired(message='请填写整数')])
    salary_max = IntegerField('最高薪水（单位：千元）', validators=[DataRequired(message='请填写整数')])
    city = StringField('工作城市', validators=[DataRequired(message='请填写内容'),
                                           Length(0, 16, message='最多16个字符')])
    tags = StringField('职位标签(用逗号区隔)', validators=[Length(0, 64)])
    exp = SelectField('工作年限', choices=[(i, i) for i in EXP])
    education = SelectField('学历要求', choices=[(i, i) for i in EDUCATION])
    treatment = CKEditorField('职位待遇', validators=[Length(0, 256, message='最多256个字符')])
    description = CKEditorField('职位描述', validators=[DataRequired(message='请填写内容')])
    is_enable = SelectField('发布', choices=[(True, '立即发布'), (False, '暂不发布')], coerce=bool)
    submit = SubmitField('提交')

    def validate_salary_min(self, field):
        if field.data <= 0 or field.data > 100:
            raise ValidationError('须填写0～100之间的整数')
        if self.salary_max.data and field.data >= self.salary_max.data:
            raise ValidationError('需要小于最高薪水')

    def validate_salary_max(self, field):
        if field.data <= 0 or field.data > 100:
            raise ValidationError('须填写0~100之间的整数')
        if self.salary_min.data and field.data <= self.salary_min.data:
            raise ValidationError('需要大于最低薪水')

    def create_job(self, company_id):
        job = Job()
        self.populate_obj(job)
        job.company_id = company_id
        db.session.add(job)
        db.session.commit()
        return job

    def update_job(self, job):
        self.populate_obj(job)
        db.session.add(job)
        db.session.commit()
        return job


def random_name():
    key = ''.join([chr(random.randint(48, 122)) for _ in range(20)])
    h = hmac.new(key.encode('utf-8'), digestmod='MD5')
    return h.hexdigest() + '.'
