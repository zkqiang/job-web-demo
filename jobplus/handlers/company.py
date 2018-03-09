#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, \
    redirect, url_for, flash, request, current_app
from ..forms import JobForm, RegisterCompanyForm, CompanyDetailForm, FINANCE_STAGE
from ..models import Company, Job

company = Blueprint('company', __name__, url_prefix='/company')


@company.route('/register')
def register():
    form = RegisterCompanyForm()
    if form.validate_on_submit():
        form.create_company()
        flash('注册成功，请登录', 'success')
        return redirect(url_for('.login'))
    return render_template('company/register.html', active='company_register')


@company.route('/')
def index():
    page = request.args.get('page', default=1, type=int)
    content = Company.query.order_by(Company.updated_at.desc()).paginate(
        page=page, per_page=current_app.config['INDEX_PER_PAGE'], error_out=False)
    return render_template('company/index.html', content=content)


@company.route('/<int:company_id>')
def detail(company_id):
    company_data = Company.query.get_or_404(company_id)
    return render_template('company/detail.html', company=company_data)


@company.route('/<int:company_id>/edit', methods=['GET', 'POST'])
def edit(company_id):
    company_data = Company.query.get_or_404(company_id)
    form = CompanyDetailForm(obj=company_data)
    if form.is_submitted():
        form.update_detail(company_data)
        flash('公司信息更新成功', 'success')
        return redirect(url_for('company.edit', company_id=company_data.id))
    return render_template('company/edit.html', form=form, company=company_data)


@company.route('/<int:company_id>/jobs')
def jobs(company_id):
    Company.query.get_or_404(company_id)
    page = request.args.get('page', default=1, type=int)
    content = Job.query.filter(company_id=company_id).order_by(Job.updated_at.desc()).paginate(
        page=page, per_page=current_app.config['LIST_PER_PAGE'], error_out=False)
    return render_template('company/jobs.html', content=content)


@company.route('/<int:company_id>/job/create', methods=['GET', 'POST'])
def create_job(company_id):
    form = JobForm()
    if form.is_submitted():
        form.create_job(company_id)
        flash('职位创建成功', 'success')
        return render_template('company/job.html')
    return render_template('company/create_job.html')


@company.route('/<int:company_id>/job/<int:job_id>/edit', methods=['GET', 'POST'])
def edit_job(company_id, job_id):
    company_data = Company.query.get_or_404(company_id)
    job_data = Company.query.get_or_404(job_id)
    form = JobForm(obj=job_data)
    if form.is_submitted():
        form.update_job(job_data)
        flash('职位更新成功', 'success')
        return redirect(url_for('company.edit', company_id=company_data.id))
    return render_template('company/edit.html', form=form, company=company_data, job=job_data)


@company.route('/<int:company_id>/resumes')
def resumes(company_id):
    return render_template('company/resumes.html')
