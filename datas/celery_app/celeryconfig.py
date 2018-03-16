#!/usr/bin/env python
# -*- coding: utf-8 -*-

from celery.schedules import crontab

BROKER_URL = 'redis://127.0.0.1:6379'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379'

FORKED_BY_MULTIPROCESSING = 1

CELERY_TIMEZONE = 'Asia/Shanghai'

CELERY_IMPORTS = (
    'celery_app.task'
)

CELERYBEAT_SCHEDULE = {
    'at-time': {
        'task': 'celery_app.task.add',
        'schedule': crontab(hour=0, minute=10)
    }
}
