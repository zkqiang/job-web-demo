#!/usr/bin/env python
# -*- coding: utf-8 -*-
import redis
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from .config import MYSQL_URL, HOST, PORT, KEY_NAME
import sys
sys.path.append('..')
from job_web.models import Company


class SqlOperator(object):

    def __init__(self):
        engine = create_engine(MYSQL_URL)
        db_session = sessionmaker(bind=engine)
        self.session = db_session()
        self.logger = logging.getLogger('root')

    def add_commit(self, data):
        self.session.add(data)
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            self.logger.error(e)

    def get_company_id(self, name):
        try:
            company = self.session.query(Company).filter(
                Company.name == name).one()
            return company.id
        except NoResultFound:
            return None


class Dupefilter(object):

    def __init__(self):
        self.key = KEY_NAME
        self._conn = redis.StrictRedis(
            host=HOST, port=PORT, max_connections=20, decode_responses=True)

    def add(self, url):
        return self._conn.sadd(self.key, url)
