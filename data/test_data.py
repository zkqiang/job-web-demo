#!/usr/bin/env python
# -*- coding: utf-8 -*-

from faker import Faker
from job_web.models import db, User, Company, Job
import random
from job_web.forms import EXP, EDUCATION, FINANCE_STAGE, FIELD
import time

fake = Faker('zh_CN')
fake_en = Faker()


class FakerData(object):

    def fake_user(self):
        for _ in range(30):
            c = User()
            c.id = int(time.time() * 100000000)
            c.name = fake.word()
            c.email = fake_en.email()
            # c.phone = random.randint(13900000000, 13999999999)
            c.password = '123456'
            db.session.add(c)
            db.session.commit()

            d = Company()
            d.name = fake.word() + fake.word() + fake.word() + fake.word()
            d.email = fake_en.email()
            # d.phone = random.randint(13900000000, 13999999999)
            d.password = '123456'
            d.logo = 'https://www.zhipin.com/v2/chat_v2/images/v2/defaultlogov2.jpg'
            d.address = fake.word()
            d.field = random.choice(FIELD)
            d.finance_stage = random.choice(FINANCE_STAGE)
            d.description = fake.word()
            d.details = fake.word()
            db.session.add(d)
            db.session.commit()

    def fake_job(self):
        companies = Company.query.all()
        for _ in range(50):
            job = Job()
            job.name = fake.word() + '工程师'
            job.salary_min, job.salary_max = random.choice([
                (3, 5), (5, 8), (7, 10), (10, 30), (50, 100)])
            job.company = random.choice(companies)
            job.exp = random.choice(EXP)
            job.education = random.choice(EDUCATION)
            job.city = random.choice(('北京', '上海', '广州'))
            job.description = fake.word()
            job.treatment = fake.word()
            job.tags = '%s,%s,%s,%s' % (fake.word(), fake.word(), fake.word(), fake.word())
            db.session.add(job)
            db.session.commit()


def run():
    f = FakerData()
    f.fake_user()
    f.fake_job()
