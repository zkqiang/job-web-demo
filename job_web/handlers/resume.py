#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, current_app, redirect, url_for, flash, request
from flask_login import current_user
from ..models import Delivery
from ..decorators import company_required

resume = Blueprint('resume', __name__, url_prefix='/resume')


@resume.route('/<int:resume_id>')
def resume_detal(resume_id):
    return render_template('resume/detail.html')


@resume.route('/<int:resume_id>')
@company_required
def resumes(resume_id):
    page = request.args.get('page', default=1, type=int)
    pagination = current_user.resumes.order_by(Job.updated_at.desc()).paginate(
        page=page, per_page=current_app.config['LIST_PER_PAGE'], error_out=False)
    return render_template('company/resumes.html', pagination=pagination, active='resumes')
