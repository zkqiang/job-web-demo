#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, current_app, redirect, url_for, flash

resume = Blueprint('resume', __name__, url_prefix='/resume')


@resume.route('/myresume')
def myresume():
    return render_template('resume/resume.html')


@resume.route('/<int:resume_id>')
def resume_detal(resume_id):
    return render_template('resume/detail.html')


@resume.route('/create', methods=['GET', 'POST'])
def create_resume():
    return render_template('resume/create.html')


@resume.route('/<int:resume_id>/edit', methods=['GET', 'POST'])
def edit_resume(resume_id):
    return render_template('resume/edit.html')
