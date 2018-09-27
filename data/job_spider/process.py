#!/usr/bin/env python
# -*- coding: utf-8 -*-

from multiprocessing import Process
from .spider import LaGouSpider
from .config import LOGGING_CONF
from .dbop import SqlOperator
import logging
from logging.config import dictConfig
from faker import Faker
from datetime import datetime, timedelta
import queue
import random
import sys
sys.path.append('..')
from job_web.models import Company, Job


class SpiderProcess(Process):
    """爬虫进程"""

    def __init__(self, data_queue):
        Process.__init__(self)
        self.data_queue = data_queue

    def iter_spider(self, spider):
        """对爬虫类的`crawl`方法进行迭代，数据送入队列传给另一进程"""
        generator = spider.crawl()
        if generator:
            for result in spider.crawl():
                if not result:
                    continue
                self.data_queue.put(result)
        self.data_queue.put('end')
        logger = logging.getLogger('root')
        logger.info('%s 爬虫已结束' % spider.__class__.__name__)

    def run(self):
        dictConfig(LOGGING_CONF)
        logger = logging.getLogger('root')
        logger.info('进程-I 已启动')
        spider = LaGouSpider()
        self.iter_spider(spider)


class WriterProcess(Process):
    """写数据进程"""

    def __init__(self, data_queue):
        Process.__init__(self)
        self.data_queue = data_queue

    def run(self):
        dictConfig(LOGGING_CONF)
        logger = logging.getLogger('root')
        logger.info('进程-II 已启动')
        fake_en = Faker()
        company_id = 1
        sql = SqlOperator()
        while True:
            try:
                result = self.data_queue.get(timeout=600)
            except queue.Empty:
                logger.info('Done!')
                return 
            if result.get('type') == 'company':
                logger.debug(result)
                if result.get('company_id'):
                    logger.debug('已存在的企业ID: %s' % result.get('company_id'))
                    company_id = result.get('company_id')
                    continue
                company = Company()
                attrs = ['name', 'logo', 'address', 'field', 'finance_stage',
                         'description', 'details', 'website']
                list(map(lambda k: setattr(company, k, result.get(k)), attrs))
                company.email = fake_en.email()
                # company.phone = random.randint(13000000000, 18999999999)
                company.password = '123456'
                sql.add_commit(company)
                company_id = sql.get_company_id(result['name'])

            elif result.get('type') == 'job':
                logger.debug(result)
                job = Job()
                try:
                    job.salary_min, job.salary_max = result.get(
                        'salary').replace('k', '').replace('K', '').split('-')
                except ValueError:
                    continue
                job.company_id = company_id
                attrs = ['name', 'exp', 'education', 'city', 'description',
                         'treatment', 'tags']
                list(map(lambda k: setattr(job, k, result.get(k)), attrs))
                random_time = datetime.now() + timedelta(minutes=random.randint(-30000, 500))
                job.updated_at = random_time
                job.created_at = random_time
                sql.add_commit(job)
