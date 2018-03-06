#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, current_app, redirect, url_for, flash

admin = Blueprint('admin', __name__, url_prefix='/admin')


@admin.route('/')
def admin_index():
    return render_template('admin/index.html')


@admin.route('/user')
def admin_user():
    return render_template('admin/user.html')


@admin.route('/company')
def admin_company():
    return render_template('admin/company.html')


@admin.route('/job')
def admin_job():
    return render_template('admin/job.html')


@admin.route('/resume')
def admin_resume():
    return render_template('admin/resume.html')
