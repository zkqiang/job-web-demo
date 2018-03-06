#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, current_app, redirect, url_for, flash

user = Blueprint('user', __name__, url_prefix='/user')


@user.route('/<int:user_id>')
def user_detail(user_id):
    return render_template('user/detail.html')


@user.route('/<int:user_id>/edit', methods=['GET', 'POST'])
def edit_user(user_id):
    return render_template('user/edit.html')


@user.route('/<int:user_id>/delivery')
def user_delivery(user_id):
    return render_template('user/delivery.html')
