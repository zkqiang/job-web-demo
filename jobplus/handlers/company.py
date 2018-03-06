#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, current_app, redirect, url_for, flash

company = Blueprint('company', __name__, url_prefix='/company')


@company.route('/')
def company_list():
    return render_template('company/list.html')


@company.route('/<int:company_id>')
def company_detail(company_id):
    return render_template('company/detail.html')


@company.route('/<int:company_id>/edit', methods=['GET', 'POST'])
def edit_company(company_id):
    return render_template('company/edit.html')


@company.route('/<int:company_id>/job')
def company_job(company_id):
    return render_template('company/job.html')


@company.route('/<int:company_id>/resume')
def company_resume(company_id):
    return render_template('company/job.html')
