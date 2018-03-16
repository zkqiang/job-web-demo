#!/usr/bin/env python
# -*- coding: utf-8 -*-

from celery_app import app
import sys
sys.path.append('..')
from datas.run_spider import main


@app.task(bind=True)
def start(self):
    try:
        main()
    except Exception as e:
        self.retry(exc=e, countdown=30, max_retries=10)
