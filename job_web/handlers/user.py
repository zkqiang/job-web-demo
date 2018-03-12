#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, flash, redirect, url_for, request, current_app
from flask_login import current_user, login_required
from ..forms import UserDetailForm, RegisterUserForm, UserResumeForm
from ..models import Delivery

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
        form.update_detail(current_user)
        flash('个人信息更新成功', 'success')
        return redirect(url_for('user.edit'))
    return render_template('user/edit.html', form=form, active='manage', panel='edit')


@user.route('/resume', methods=['GET', 'POST'])
@login_required
def resume():
    if not current_user.is_user():
        return redirect(url_for("front.index"))
    form = UserResumeForm()
    resume_url = current_user.resume
    if form.validate_on_submit():
        resume_url = form.upload_resume(current_user)
    return render_template('user/resume.html', form=form, file_url=resume_url, active='manage', panel='resume')


@user.route('/delivery')
@login_required
def delivery():
    if not current_user.is_user():
        return redirect(url_for("front.index"))
    status = request.args.get('status', None)
    page = request.args.get('page', default=1, type=int)
    if status:
        pagination = current_user.delivery.filter_by(status=status).order_by(Delivery.updated_at.desc()).paginate(
            page=page, per_page=current_app.config['LIST_PER_PAGE'], error_out=False)
    else:
        pagination = current_user.delivery.order_by(Delivery.updated_at.desc()).paginate(
            page=page, per_page=current_app.config['LIST_PER_PAGE'], error_out=False)
    return render_template('user/delivery.html', pagination=pagination,
                           active='manage', panel='delivery', status=status)


@user.errorhandler(413)
def page_not_found(error):
    flash('文件大小超过限制', 'warning')
    return redirect(request.path)
