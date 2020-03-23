# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, abort,\
    current_app, redirect, url_for, flash, request
from flask_login import current_user, login_required
from ..decorators import company_required
from ..models import Job, db, Delivery
from ..forms import EXP, JobForm

job = Blueprint('job', __name__, url_prefix='/job')


@job.route('/')
def index():
    page = request.args.get('page', default=1, type=int)
    kw = request.args.get('kw')
    flt = {Job.is_enable is True}
    if kw is not None and kw != '':
        flt.update({Job.name.like('%{}%'.format(kw))})
    pagination = Job.query.filter(*flt).order_by(
            Job.created_at.desc()).paginate(
                page=page,
                per_page=current_app.config['JOB_INDEX_PER_PAGE'],
                error_out=False
            )
    return render_template('job/index.html', pagination=pagination,
                           kw=kw, filter=EXP, active='job')


@job.route('/<int:job_id>')
def detail(job_id):
    job_obj = Job.query.get_or_404(job_id)
    if not job_obj.is_enable and job_obj.company_id != current_user.id:
        abort(404)
    return render_template('job/detail.html', job=job_obj)


@job.route('/<int:job_id>/apply', methods=['GET', 'POST'])
@login_required
def apply(job_id):
    job_obj = Job.query.get_or_404(job_id)
    if not current_user.is_user():
        abort(404)
    if not current_user.resume:
        flash('请先上传简历', 'warning')
        return redirect(url_for('user.resume'))
    elif job_obj.is_applied():
        flash('已经投递过该职位', 'warning')
        return redirect(url_for('job.detail', job_id=job_id))
    delivery = Delivery(
        job_id=job_id,
        user_id=current_user.id,
        company_id=job_obj.company.id,
        resume=current_user.resume
    )
    db.session.add(delivery)
    db.session.commit()
    flash('简历投递成功', 'success')
    return redirect(url_for('job.detail', job_id=job_id))


@job.route('/create', methods=['GET', 'POST'])
@company_required
def create():
    form = JobForm()
    if form.validate_on_submit():
        company_id = current_user.id
        form.create_job(company_id)
        flash('职位创建成功', 'success')
        return redirect_job_index()
    return render_template('job/create.html', form=form, active='manage', panel='create')


@job.route('/<int:job_id>/edit', methods=['GET', 'POST'])
@company_required
def edit(job_id):
    job_obj = Job.query.get_or_404(job_id)
    if job_obj.company_id != current_user.id and not current_user.is_admin():
        abort(404)
    form = JobForm(obj=job_obj)
    if form.validate_on_submit():
        form.update_job(job_obj)
        flash('职位更新成功', 'success')
        return redirect_job_index()
    return render_template('job/edit.html', form=form, job_id=job_id)


@job.route('/<int:job_id>/delete', methods=['GET', 'POST'])
@company_required
def delete(job_id):
    job_obj = Job.query.get_or_404(job_id)
    if job_obj.company_id != current_user.id and not current_user.is_admin():
        abort(404)
    db.session.delete(job_obj)
    db.session.commit()
    flash('职位删除成功', 'success')
    return redirect_job_index()


@job.route('<int:job_id>/disable')
@company_required
def disable(job_id):
    job_obj = Job.query.get_or_404(job_id)
    if not current_user.is_admin() and current_user.id != job_obj.company.id:
        abort(404)
    if not job_obj.is_enable:
        flash('职位已下线', 'warning')
    else:
        job_obj.is_enable = False
        db.session.add(job_obj)
        db.session.commit()
        flash('职位下线成功', 'success')
    return redirect_job_index()


@job.route('<int:job_id>/enable')
@company_required
def enable(job_id):
    job_obj = Job.query.get_or_404(job_id)
    if not current_user.is_admin() and current_user.id != job_obj.company.id:
        abort(404)
    if job_obj.is_enable:
        flash('职位已上线', 'warning')
    else:
        job_obj.is_enable = True
        db.session.add(job_obj)
        db.session.commit()
        flash('职位上线成功', 'success')
    return redirect_job_index()


def redirect_job_index():
    if current_user.is_admin():
        return redirect(url_for('admin.job'))
    elif current_user.is_company():
        return redirect(url_for('company.jobs'))
    else:
        return redirect(url_for('front.index'))
