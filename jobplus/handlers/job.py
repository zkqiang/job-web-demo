#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, current_app, redirect, url_for, flash

job = Blueprint('job', __name__, url_prefix='/job')


@job.route('/')
def job_list():
    return render_template('job/list.html')


@job.route('/<int:job_id>')
def job_detail(job_id):
    return render_template('job/detail.html')


@job.route('/create', methods=['GET', 'POST'])
def create_job():
    return render_template('job/create.html')


@job.route('/<int:job_id>/edit', methods=['GET', 'POST'])
def edit_job(job_id):
    return render_template('job/edit.html')


@job.route('/<int:job_id>/delete', methods=['GET', 'POST'])
def delete_job(job_id):
    pass
