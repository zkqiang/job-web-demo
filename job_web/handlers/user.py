#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from ..forms import UserDetailForm, RegisterUserForm
from ..models import User, ROLE_USER

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
    if not current_user != ROLE_USER:
        flash("您不是个人用户", "warning")
        return redirect(url_for("front.index"))
    form = UserDetailForm(obj=current_user)
    if form.validate_on_submit():
        form.update_detail(current_user)
        flash('个人信息更新成功', 'success')
    return render_template('user/edit.html', form=form)


# @user.route('/<int:user_id>/delivery')
# @user_required
# def user_delivery(user_id):
#     return render_template('user/delivery.html')

