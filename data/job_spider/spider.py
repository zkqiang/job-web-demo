#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import time
import re
import json
import random
import logging
from lxml import etree
from html import unescape
from .dbop import SqlOperator, Dupefilter
from .config import UA


class LaGouSpider(object):
    """拉勾网"""

    def __init__(self):
        # 需要指定cookie，否则会出错
        self.headers = UA.copy()
        self.headers.update({
            'Referer': 'https://www.lagou.com/gongsi/',
            'Cookie': 'user_trace_token=20170912104426-9ba6e9c6-3053-45fd-9025-681bef8b0c8f; '
                      'LGUID=20170916191219-e783b163-9acf-11e7-952a-525400f775ce; '
                      'index_location_city=%E6%B7%B1%E5%9C%B3; TG-TRACK-CODE=index_search; '
                      '_gid=GA1.2.1386711592.1505703954; _ga=GA1.2.351899359.1505560343; '
                      'Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1505560343,1505703955; '
                      'Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1505703988; '
                      'LGRID=20170918110627-5c595dd3-9c1e-11e7-9196-5254005c3644; '
                      'JSESSIONID=ABAAABAAAIAACBIF3290756E031DCE7CCEA3986CB372F49; '
                      'SEARCH_ID=d30eb13562344eb9b5f6b8f05eb2cefc'
        })
        self.logger = logging.getLogger('root')
        # 同一爬虫连续请求的最短间隔
        self.request_sleep = 7
        # 用于记录最近一次请求的时间戳
        self._time_recode = 0
        self._redis = Dupefilter()
        self._sql = SqlOperator()

    def crawl(self):
        page = 1
        while True:
            companies = self._get_company_data(page)
            if not companies:
                return True
            for c in companies:
                result, company_id = self._parse_company_data(c)
                yield result if result else {'type': 'company', 'company_id': company_id}
                job_page = 1
                counter = 0
                # 每个公司的职位只随机爬前N个
                total = random.randint(5, 30)
                while counter < total:
                    jobs = self._get_job_data(c['companyId'], job_page)
                    if not jobs:
                        break
                    for j in jobs:
                        job_result = self._parse_job_data(j)
                        counter += 1
                        if not job_result:
                            counter = total
                            break
                        yield job_result
                    job_page += 1
            page += 1

    def _get_company_data(self, page):
        url = 'https://www.lagou.com/gongsi/0-0-0.json'
        params = {'first': 'false', 'pn': page, 'sortField': 0, 'havemark': 0}
        resp = self._request('post', url, data=params)
        # 解析详情页的编号，进一步分析详情页
        resp_data = json.loads(resp.text)
        return resp_data['result']

    def _get_job_data(self, company_id, page):
        job_url = 'https://www.lagou.com/gongsi/searchPosition.json'
        job_params = {'companyId': company_id, 'pageNo': page,
                      'positionFirstType': '全部', 'pageSize': 10, 'schoolJob': 'false'}
        job_resp = self._request('post', job_url, data=job_params)
        job_resp_data = json.loads(job_resp.text)
        return job_resp_data['content']['data']['page']['result']

    def _parse_company_data(self, data):
        result = dict()
        detail_url = 'https://www.lagou.com/gongsi/%s.html' % data['companyId']
        company_id = self._sql.get_company_id(data['companyShortName'])
        if not company_id:
            result = {
                'type': 'company',
                'name': data['companyShortName'],
                'description': data['companyFeatures'],
                'field': data['industryField'].split(',')[0],
                'finance_stage': data['financeStage'],
                'address': data['city'],
                'logo': 'https://www.lgstatic.com/thumbnail_300x300/' + data['companyLogo']
            }
            result.update(self._parse_company_detail(detail_url))
        return result, company_id

    def _parse_job_data(self, data):
        detail_url = 'https://www.lagou.com/jobs/%s.html' % data['positionId']
        if not self._redis.add(detail_url):
            return None
        job_result = {
            'type': 'job',
            'name': data['positionName'],
            'salary': data['salary'],
            'city': data['city'],
            'exp': data['workYear'],
            'education': data['education'],
            'treatment': '，'.join(data['companyLabelList']),
            'tags': re.sub(r'[\s、;]', ',', data['positionAdvantage']),
        }
        job_result.update(self._parse_job_detail(detail_url))
        return job_result

    def _parse_company_detail(self, detail_url):
        resp = self._request('get', detail_url)
        resp.encoding = resp.apparent_encoding
        html = etree.HTML(resp.text)
        name = html.xpath('//div[@class="company_main"]/h1/a/text()')
        # 这里最好先判断一下，以免没提取到出现异常
        if not name:
            self.logger.debug('请求到错误页面')
            time.sleep(30)
            return self._parse_company_detail(detail_url)
        # 返回的键必须包含这些，否则写入会报错
        supply = {
            'details': unescape(str(etree.tostring(html.xpath(
                '//span[@class="company_content"]')[0]), encoding='utf8')).replace(
                '<span class="company_content">', '').replace('\n', '').replace('\xa0', ''),
            'website': html.xpath('//div[@class="company_main"]/a[1]/@href')[0].split('?')[0],
        }
        return supply

    def _parse_job_detail(self, url):
        resp = self._request('get', url)
        resp.encoding = resp.apparent_encoding
        html = etree.HTML(resp.text)
        title = html.xpath('//span[@class="name"]/text()')
        if not title:
            self.logger.debug('请求到错误页面')
            time.sleep(30)
            return self._parse_job_detail(url)
        supply = {
            'description': unescape(str(etree.tostring(
                html.xpath('//*[@id="job_detail"]/dd[2]/div')[0]), encoding='utf8')).replace(
                '<span class="company_content">', '').replace('\n', '').replace('\xa0', '')
        }
        return supply

    def _request(self, method='get', url=None, encoding=None, **kwargs):
        while True:
            # 没有指定头部则使用默认头部
            if not kwargs.get('headers'):
                kwargs['headers'] = self.headers
            # 随机生成系数对间隔产生变化
            rand_multi = random.uniform(0.8, 1.2)
            # 距离上次请求的间隔
            interval = time.time() - self._time_recode
            # 如间隔小于最短间隔，则进行等待
            if interval < self.request_sleep:
                time.sleep((self.request_sleep - interval) * rand_multi)
            resp = getattr(requests, method)(url, **kwargs)
            # 请求完重新记录时间戳
            self._time_recode = time.time()
            if encoding:
                resp.encoding = encoding
            if '频繁' in resp.text:
                self.logger.debug('请求频繁重试')
                time.sleep(20)
            else:
                break
        return resp
