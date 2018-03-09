#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from ..models import Job, User, Company
from ..forms import LoginForm

front = Blueprint('front', __name__)


@front.route('/')
def index():
    jobs = Job.query.filter(Job.is_enable.is_(True)).order_by(Job.updated_at.desc()).limit(9)
    companies = Company.query.filter(Company.is_enable.is_(True)).order_by(Company.updated_at).limit(8)
    return render_template('index.html', active='index', jobs=jobs, companies=companies)


@front.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_data = User.query.filter_by(email=form.email.data).first()
        if not user_data:
            user_data = User.query.filter_by(email=form.email.data).first()
            if not user_data:
                flash('登录信息有误，请重新登录', 'error')
                return redirect(url_for('.login'))
        if not user_data.is_enable:
            flash('该用户不可用，请联系网站管理员', 'error')
            return redirect(url_for('.login'))
        login_user(user_data, form.remember_me.data)
        flash('登录成功', 'success')
        next_page = request.args.get('next')
        return redirect(next_page or url_for('.index'))
    return render_template('login.html', form=form, active='login')


@front.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('您已经退出登录', 'success')
    return redirect(url_for('.index'))
