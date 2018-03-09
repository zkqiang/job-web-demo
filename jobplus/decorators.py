#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import wraps
from flask import abort, current_app
from flask_login import current_user
from .forms import ROLE_USER, ROLE_COMPANY, ROLE_ADMIN


def role_required(role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role < role:
                abort(404)
            return func(*args, **kwargs)
        return wrapper
    return decorator


# user_required = role_required(ROLE_USER)
company_required = role_required(ROLE_COMPANY)
admin_required = role_required(ROLE_ADMIN)
