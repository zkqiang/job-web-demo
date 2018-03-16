#!/usr/bin/env python
# -*- coding: utf-8 -*-

from celery import Celery

app = Celery('job_web')
app.config_from_object('celery_app.celeryconfig')
