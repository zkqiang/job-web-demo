#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from ..forms import UserDetailForm, RegisterUserForm, UserResumeForm
from ..app import uploaded_pdf
from ..models import db
import random
import hmac

user = Blueprint('user', __name__, url_prefix='/user')


@user.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('front.index'))
    form = RegisterUserForm()
    if form.validate_on_submit():
        form.create_user()
        flash('注册成功，请登录', 'success')
        return redirect(url_for('front.login'))
    return render_template('user/register.html', form=form, active='user_register')


@user.route('/account', methods=['GET', 'POST'])
@login_required
def edit():
    if not current_user.is_user():
        return redirect(url_for("front.index"))
    form = UserDetailForm(obj=current_user)
    if form.validate_on_submit():
        form.update_detail()
        flash('个人信息更新成功', 'success')
        return redirect(url_for('user.edit'))
    return render_template('user/edit.html', form=form, panel='edit')


@user.route('/resume', methods=['GET', 'POST'])
@login_required
def resume():
    if not current_user.is_user():
        return redirect(url_for("front.index"))
    form = UserResumeForm()
    resume_url = None
    if form.validate_on_submit():
        print(form.resume.data)
        filename = uploaded_pdf.save(form.resume.data, name=random_name())
        resume_url = uploaded_pdf.url(filename)
        current_user.resume = resume_url
        print(filename, resume_url)
        db.session.add(current_user)
        db.session.commit()
    return render_template('user/resume.html', form=form, file_url=resume_url, panel='resume')


def random_name():
    key = ''.join([chr(random.randint(48, 122)) for _ in range(20)])
    h = hmac.new(key.encode('utf-8'), digestmod='MD5')
    return h.hexdigest() + '.'
