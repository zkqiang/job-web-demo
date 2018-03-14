#!/usr/bin/env python
# -*- coding: utf-8 -*-

from threading import Thread
from multiprocessing import Process
from job_spider.spider import SpiderMeta
import queue
import logging
import time
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import random
import sys
sys.path.append('..')
from job_web.models import Company, Job


class SpiderProcess(Process):
    """爬虫进程"""

    def __init__(self, data_queue):
        Process.__init__(self)
        self.data_queue = data_queue
        self.logger = logging.getLogger('root')

    def set_logging(self):
        """设置日志格式"""
        self.logger = logger = logging.getLogger('root')
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

    def iter_spider(self, spider):
        """对爬虫类的`crawl`方法进行迭代，数据送入队列传给另一进程"""
        generator = spider.crawl()
        if generator:
            for result in spider.crawl():
                if not result:
                    continue
                # 去除内容里的空格换行
                # for key in result.keys():
                #     result[key] = re.sub(r'\s+', '', result[key])
                self.data_queue.put(result)
        self.logger.info('%s 爬虫已结束' % spider.__class__.__name__)

    def run(self):
        """对每个爬虫类启动单独线程"""
        self.set_logging()
        spiders = [cls() for cls in SpiderMeta.spiders]
        spider_count = len(spiders)
        threads = []
        for i in range(spider_count):
            t = Thread(target=self.iter_spider, args=(spiders[i], ))
            t.setDaemon(True)
            t.start()
            threads.append(t)
        while True:
            time.sleep(1)


class WriterProcess(Process):
    """写数据进程"""

    def __init__(self, data_queue):
        Process.__init__(self)
        self.data_queue = data_queue

    def run(self):
        fake_en = Faker()
        company_id = ''
        engine = create_engine('mysql+mysqldb://root@localhost:3306/job_web?charset=utf8')
        db_session = sessionmaker(bind=engine)
        session = db_session()
        while True:
            try:
                result = self.data_queue.get(timeout=90)
                if result.get('type') == 'company':
                    d = Company()
                    d.name = result.get('name')
                    d.email = fake_en.email()
                    # d.phone = random.randint(13900000000, 13999999999)
                    d.password = '123456'
                    d.logo = result.get('logo')
                    d.address = result.get('address')
                    d.field = result.get('field')
                    d.finance_stage = result.get('finance_stage')
                    d.description = result.get('description')
                    d.details = result.get('details')
                    d.website = result.get('website')
                    session.add(d)
                    session.commit()
                    company_id = session.query(Company).filter(
                        Company.name == result.get('name')).one().id

                elif result.get('type') == 'job':
                    job = Job()
                    job.name = result.get('name')

                    job.salary_min, job.salary_max = result.get(
                        'salary').replace('k', '').replace('K', '').split('-')
                    job.company_id = company_id
                    job.exp = result.get('exp')
                    job.education = result.get('education')
                    job.city = result.get('city')
                    job.description = result.get('description')
                    job.treatment = result.get('treatment')
                    job.tags = result.get('tags')
                    random_time = datetime.now() + timedelta(minutes=random.randint(-30000, 500))
                    job.updated_at = random_time
                    job.created_at = random_time
                    session.add(job)
                    session.commit()
            except queue.Empty:
                print('Done!')
