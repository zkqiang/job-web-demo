#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, flash, redirect, url_for
from ..forms import UserDetailForm, RegisterUserForm
from ..models import User

user = Blueprint('user', __name__, url_prefix='/user')


@user.route('/register')
def register():
    form = RegisterUserForm()
    if form.validate_on_submit():
        form.create_user()
        flash('注册成功，请登录', 'success')
        return redirect(url_for('.login'))
    return render_template('user/register.html', active='company_register')


@user.route('/<int:user_id>detail')
def detail(user_id):
    user_data = User.query.get_or_404(user_id)
    form = UserDetailForm(obj=user_data)
    return render_template('user/detail.html', form=form)


# @user.route('/<int:user_id>/edit', methods=['GET', 'POST'])
# @user_required
# def edit_user(user_id):
#     return render_template('user/edit.html')
#
#
# @user.route('/<int:user_id>/delivery')
# @user_required
# def user_delivery(user_id):
#     return render_template('user/delivery.html')

