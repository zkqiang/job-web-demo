from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import IntegerField, PasswordField, SelectField, \
    StringField, SubmitField, TextAreaField, ValidationError, BooleanField
from wtforms.validators import Email, EqualTo, Regexp, Length, URL, DataRequired
from .models import User, Company, db, Job
from .app import uploaded_pdf

FINANCE_STAGE = ['未融资', '天使轮', 'A轮', 'B轮', 'C轮', 'D轮及以上', '上市公司', '不需要融资']
FIELD = ['移动互联网', '电子商务', '金融', '企业服务', '教育', '文化娱乐', '游戏', 'O2O', '硬件']
EXP = ['应届毕业生', '3年及以下', '3-5年', '5-10年', '10年以上', '不限']
EDUCATION = ['不限学历', '专科', '本科', '硕士', '博士']

ROLE_USER = 10
ROLE_COMPANY = 20
ROLE_ADMIN = 30


class RegisterUserForm(FlaskForm):

    name = StringField('姓名', validators=[DataRequired(message='请填写内容'),
                                         Length(4, 16, message='长度要在4～16个字符之间')])
    email = StringField('邮箱', validators=[DataRequired(message='请填写内容'),
                                          Email(message='请输入合法的email地址')])
    password = PasswordField('密码', validators=[DataRequired(message='请填写密码'),
                                               Length(6, 24, message='长度须在6～24个字符之间'),
                                               Regexp(r'^[a-zA-Z]+\w+', message='只能使用英文、数字、下划线，并以英文开头')])
    repeat_password = PasswordField('重复密码', validators=[DataRequired(message='请填写密码'),
                                                        EqualTo('password', message='两次密码不一致')])
    submit = SubmitField('提交')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被其他账号使用')

    def create_user(self):
        user = User()
        user.name = self.name.data
        user.email = self.email.data
        user.password = self.password.data
        user.role = ROLE_USER
        db.session.add(user)
        db.session.commit()
        return user


class RegisterCompanyForm(FlaskForm):

    name = StringField('企业名称', validators=[DataRequired(message='请填写内容'),
                                           Length(4, 64, message='长度要在4～64个字符之间')])
    email = StringField('邮箱', validators=[DataRequired(message='请填写内容'),
                                          Email(message='请输入合法的email地址')])
    password = PasswordField('密码', validators=[DataRequired(message='请填写密码'),
                                               Length(6, 24, message='长度须在6～24个字符之间'),
                                               Regexp(r'^[a-zA-Z]+\w+', message='只能使用英文、数字、下划线，并以英文开头')])
    repeat_password = PasswordField('重复密码', validators=[DataRequired(message='请填写密码'),
                                                        EqualTo('password', message='两次密码不一致')])
    submit = SubmitField('提交')

    def create_company(self):
        company = Company()
        company.name = self.name.data
        company.email = self.email.data
        company.password = self.password.data
        company.role = ROLE_COMPANY
        db.session.add(company)
        db.session.commit()
        return company


class LoginForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(message='请填写内容'),
                                          Email(message='请输入合法的email地址')])
    password = PasswordField('密码', validators=[DataRequired(message='请填写密码'),
                                               Length(6, 24, message='长度须在6～24个字符之间')])
    remember_me = BooleanField('记住登录状态')
    submit = SubmitField('登录')

    def validate_email(self, field):
        if not User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱未注册')

    def validate_password(self, field):
        user = User.query.filter_by(email=self.email.data).first()
        if user and not user.check_password(field.data):
            raise ValidationError('密码错误')


class UserDetailForm(FlaskForm):

    resume = FileField('简历上传', validators=[
                FileAllowed('pdf', '仅限PDF格式！'),
                FileRequired('文件未选择')])
    submit = SubmitField('提交')

    def update_detail(self, user):
        self.populate_obj(user)
        filename = uploaded_pdf.save(self.resume.data)
        user.resume_url = uploaded_pdf.url(filename)
        db.session.add(user)
        db.session.commit()


class CompanyDetailForm(FlaskForm):

    address = StringField('办公地址', validators=[DataRequired(message='请填写内容'),
                                              Length(2, 128, message='密码长度要在2～128个字符之间')])
    logo = StringField('公司Logo', validators=[DataRequired(message='请填写内容'),
                                             Length(1, 256, message='请确认您输入的Logo')])
    website = StringField('公司网址', validators=[DataRequired(message='请填写内容'),
                                              URL(message='请确认您输入的网址')])
    tags = StringField('职位标签(用逗号区隔)')
    description = StringField('公司简介', validators=[DataRequired(message='请填写内容')])
    company_info = CKEditorField('公司详情', validators=[DataRequired(message='请填写内容')])
    finance_stage = SelectField('融资阶段', choices=[(i, i) for i in FINANCE_STAGE])
    field = SelectField('行业领域', choices=[(i, i) for i in FIELD])
    submit = SubmitField('提交')

    def update_detail(self, company):
        self.populate_obj(company)
        db.session.add(company)
        db.session.commit()


class JobForm(FlaskForm):
    name = StringField('职位名称', validators=[DataRequired(message='请填写内容'), Length(4, 32)])
    salary_min = IntegerField('最低薪水', validators=[DataRequired(message='请填写内容'), Length(1, 3)])
    salary_max = IntegerField('最高薪水', validators=[DataRequired(message='请填写内容'), Length(1, 3)])
    city = StringField('工作城市', validators=[DataRequired(message='请填写内容'),
                                           Length(4, 8, message='长度须在4～8个字符之间')])
    tags = StringField('职位标签(用逗号区隔)', validators=[Length(0, 64)])
    stacks = StringField('技术栈标签(用逗号区隔)')
    exp = SelectField('工作年限', choices=[(i, i) for i in EXP])
    education = SelectField('学历要求', choices=[(i, i) for i in EDUCATION])
    treatment = TextAreaField('职位待遇', validators=[Length(0, 256)])
    description = CKEditorField('职位描述', validators=[DataRequired(message='请填写内容')])
    submit = SubmitField('发布')

    def create_job(self, company):
        job = Job()
        self.populate_obj(job)
        job.company_id = company.id
        db.session.add(job)
        db.session.commit()
        return job

    def update_job(self, job):
        self.populate_obj(job)
        db.session.add(job)
        db.session.commit()
        return job
