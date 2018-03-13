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
from datas.job_spider.dupefilter import RedisOperator


class SpiderMeta(type):
    """爬虫类的元类，注册子类到列表，爬虫类指定此元类才能加入进程"""

    spiders = []

    def __new__(mcs, name, bases, attrs):
        mcs.spiders.append(type.__new__(mcs, name, bases, attrs))
        return type.__new__(mcs, name, bases, attrs)


class BaseSpider(object):
    """爬虫类的基类，提供需要的属性和方法"""

    # 目标职位和城市，运行指定的参数会赋值实例属性
    # 所以爬虫代码必须有这两个属性
    job = 'Python'
    city = '上海'

    # 默认的头部
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;'
                  'q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/64.0.3282.119 Safari/537.36',
        'Upgrade-Insecure-Requests': '1',
    }
    logger = logging.getLogger('root')
    # 同一爬虫连续请求的最短间隔
    request_sleep = 5
    # 用于记录最近一次请求的时间戳
    _time_recode = 0
    _redis = RedisOperator()

    def request(self, method='get', url=None, encoding=None, **kwargs):
        """
        根据爬虫类重新封装的`requests`，可保持请求间隔，并带有默认头部
        :param method: 请求方法，`get`或`post`等
        :param url: 请求链接
        :param encoding: 指定对返回对象进行编码
        :param kwargs: 其他`requests`自带的参数
        :return: Response 对象
        """
        # 没有指定头部则使用默认头部
        if not kwargs.get('headers'):
            kwargs['headers'] = self.headers
        # 随机生成系数对间隔产生变化
        rand_multi = random.uniform(0.8, 1.2)
        # 距离上次请求的间隔
        interval = time.time()-self._time_recode
        # 如间隔小于最短间隔，则进行等待
        if interval < self.request_sleep:
            time.sleep((self.request_sleep-interval)*rand_multi)
        resp = getattr(requests, method)(url, **kwargs)
        # 请求完重新记录时间戳
        self._time_recode = time.time()
        if encoding:
            resp.encoding = encoding
        return resp


class LaGouSpider(BaseSpider, metaclass=SpiderMeta):
    """拉勾网"""

    def __init__(self):
        # 需要指定cookie，否则会出错
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

    def crawl(self):
        """
        启动爬虫的方法，爬虫类必须定义此方法，
        并将每个职位的数据用`yield`迭代返回
        """
        page = 1
        while True:
            url = 'https://www.lagou.com/gongsi/0-0-0.json'
            # 请求携带的参数
            params = {'first': 'false', 'pn': page, 'sortField': 0, 'havemark': 0}
            # 提示请求频繁则重试2次
            for _ in range(2):
                resp = self.request('post', url, data=params)
                if '频繁' not in resp.text:
                    break
                time.sleep(10)
            else:
                self.logger.error(__class__.__name__, '请求出错')
                break
            # 解析详情页的编号，进一步分析详情页
            resp_text = json.loads(resp.text)
            companies = resp_text['result']
            if not companies:
                break
            for c in companies:
                detail_url = 'https://www.lagou.com/gongsi/%s.html' % c['companyId']
                if not self._redis.add(detail_url):
                    continue
                result = {
                    'type': 'company',
                    'name': c['companyShortName'],
                    'description': c['companyFeatures'],
                    'field': c['industryField'].split(',')[0],
                    'finance_stage':  c['financeStage'],
                    'address': c['city'],
                    'logo': 'https://www.lgstatic.com/thumbnail_300x300/' + c['companyLogo']
                }
                result.update(self._parse_company_detail(detail_url))
                yield result
                job_page = 1
                while True:
                    job_url = 'https://www.lagou.com/gongsi/searchPosition.json'
                    job_params = {'companyId': c['companyId'], 'pageNo': job_page,
                                  'positionFirstType': '全部', 'pageSize': 10, 'schoolJob': 'false'}
                    job_resp = self.request('post', job_url, data=job_params)
                    job_resp_text = json.loads(job_resp.text)
                    jobs = job_resp_text['content']['data']['page']['result']
                    if not jobs:
                        break
                    for j in jobs:
                        detail_url = 'https://www.lagou.com/jobs/%s.html' % j['positionId']
                        if not self._redis.add(detail_url):
                            continue
                        job_result = {
                            'type': 'job',
                            'name': j['positionName'],
                            'salary': j['salary'],
                            'city': j['city'],
                            'exp': j['workYear'],
                            'education': j['education'],
                            'treatment': '，'.join(j['companyLabelList']),
                            'tags': re.sub(r'[\s、]', ',', j['positionAdvantage']),
                        }
                        job_result.update(self._parse_job_detail(detail_url))
                        yield job_result
                    job_page += 1
            page += 1

    def _parse_company_detail(self, detail_url):
        """解析详情页，并将数据以字典形式返回"""
        resp = self.request('get', detail_url)
        html = etree.HTML(resp.text.replace('\u2028', '').encode('utf-8'))
        name = html.xpath('//div[@class="company_main"]/h1/a/text()')
        # 这里最好先判断一下，以免没提取到出现异常
        if not name:
            self.logger.warning('%s 解析出错' % detail_url)
            return self._parse_company_detail(detail_url)
        # 返回的键必须包含这些，否则写入会报错
        supply = {
            'details': unescape(str(etree.tostring(html.xpath(
                '//span[@class="company_content"]')[0]), encoding='utf8')).replace(
                '<span class="company_content">', '').replace('\n', '').replace('\xa0', ''),
            'website': html.xpath('//div[@class="company_main"]/a[1]/@href')[0],
        }
        return supply

    def _parse_job_detail(self, url):
        resp = self.request('get', url)
        html = etree.HTML(resp.text.replace('\u2028', '').encode('utf-8'))
        title = html.xpath('//span[@class="name"]/text()')
        if not title:
            self.logger.warning('%s 解析出错' % url)
            return self._parse_job_detail(url)
        supply = {
            'description': unescape(str(etree.tostring(
                html.xpath('//*[@id="job_detail"]/dd[2]/div')[0]), encoding='utf8')).replace(
                '<span class="company_content">', '').replace('\n', '').replace('\xa0', '')
        }
        return supply


class ZhiPinSpider(BaseSpider):
    """BOSS直聘"""

    # 很容易封IP，所以间隔长一些
    request_sleep = 15

    def crawl(self):
        # 获取城市的编号构成链接
        city_code = self._parse_city()
        if not city_code:
            self.logger.error('%s 不支持目标城市' % __class__.__name__)
            return 
        search_url = 'https://www.zhipin.com/c' + city_code
        page = 1
        while True:
            params = {'query': self.job, 'page': page, 'ka': 'page-%s' % page}
            resp = self.request('get', search_url, params=params)
            html = etree.HTML(resp.text)
            detail_urls = html.xpath('//div[@class="info-primary"]/h3/a/@href')
            if not detail_urls:
                if page == 1:
                    self.logger.error('%s 可能已被BAN' % __class__.__name__)
                break
            for each in detail_urls:
                yield self._parse_detail('https://www.zhipin.com' + each)
            page += 1

    def _parse_city(self):
        """从首页索引获取对应的城市编号"""
        index_url = 'https://www.zhipin.com/common/data/city.json'
        resp = self.request('get', index_url)
        city_code = re.findall(r'"code":(\d+),"name":"%s"' % self.city, resp.text)
        if city_code:
            return city_code[0]

    def _parse_detail(self, detail_url):
        resp = self.request('get', detail_url)
        html = etree.HTML(resp.text)
        title = html.xpath('//div[@class="info-primary"]/div[@class="name"]/h1/text()')
        if not title:
            if re.search(r'您暂时无法继续访问～', resp.text):
                self.logger.error('%s 可能已被BAN' % __class__.__name__)
                return 
            self.logger.warning('%s 解析出错' % detail_url)
            return self._parse_detail(detail_url)
        result = {
            'title': title[0],
            'company': html.xpath('//div[@class="info-company"]/h3/a/text()')[0],
            'salary': html.xpath('//div[@class="info-primary"]/div[@class="name"]/span/text()')[0],
            'experience': html.xpath('//div[@class="info-primary"]/p/text()')[1].replace('经验：', ''),
            'education': html.xpath('//div[@class="info-primary"]/p/text()')[2].replace('学历：', ''),
            'url': detail_url,
            'description': html.xpath('string(//div[@class="job-sec"][1]/div)')
        }
        return result


class Job51Spider(BaseSpider):
    """前程无忧(51job)"""

    def crawl(self):
        city_code = self._parse_city()
        if not city_code:
            self.logger.error('%s 不支持目标城市' % __class__.__name__)
            return 
        url = 'http://search.51job.com/jobsearch/search_result.php'
        params = {
            'fromJs': 1,
            'jobarea': city_code,
            'keyword': self.job,
            'curr_page': 1
        }
        # 用于控制退出循环
        control = True
        while control:
            resp = self.request('get', url, params=params, encoding='GBK')
            html = etree.HTML(resp.text)
            elements = html.xpath('//*[@id="resultList"]/div[@class="el"]/p/span/a')
            for each in elements:
                # 过滤掉广告位
                if 'jobs.51job'in each.get('href'):
                    # 爬到不相关的职位后就基本爬完了
                    if self.job.lower() in each.get('title').lower():
                        yield self._parse_detail(each.get('href'))
                    else:
                        control = False
            params['curr_page'] += 1

    def _parse_city(self):
        index_url = 'http://www.51job.com/'
        resp = self.request('get', index_url, encoding='GBK')
        city_index = re.findall(r'(http://www\.51job.+?)">%s</a' % self.city, resp.text)
        if city_index:
            city_resp = self.request('get', city_index[0])
            city_code = re.findall(r'id="jobarea"\s+?value="(\d+)"', city_resp.text)[0]
            return city_code

    def _parse_detail(self, detail_url):
        resp = self.request('get', detail_url, encoding='GBK')
        html = etree.HTML(resp.text)
        title = html.xpath('//div[@class="tHeader tHjob"]/div/div/h1/text()')
        if not title:
            self.logger.warning('%s 解析出错' % detail_url)
            return self._parse_detail(detail_url)
        salary = html.xpath('//div[@class="tHeader tHjob"]/div/div/strong/text()')
        result = {
            'title': title[0],
            'company': html.xpath('//div[@class="tHeader tHjob"]/div/div/p/a/text()')[0],
            'salary': salary[0] if salary else '面议',
            'experience': html.xpath('//div[@class="jtag inbox"]/div/span/text()')[0].replace('经验', ''),
            'education': html.xpath('//div[@class="jtag inbox"]/div/span/text()')[1],
            'url': detail_url,
            'description': html.xpath('string(//div[@class="bmsg job_msg inbox"])')
        }
        return result


class LiePinSpider(BaseSpider):
    """猎聘网"""

    def crawl(self):
        city_code = self._parse_city()
        if not city_code:
            self.logger.error('%s 不支持目标城市' % __class__.__name__)
            return 
        url = 'https://www.liepin.com/zhaopin/'
        params = {
            'dqs': city_code,
            'key': self.job,
            'headckid': '7d66a97979abf7ec',
            'curPage': 0
            }

        control = True
        while control:
            resp = self.request('get', url, params=params)
            html = etree.HTML(resp.text)
            elements = html.xpath('//div[@class="job-info"]/h3/a')
            for each in elements:
                if '/job/' in each.get('href'):
                    if self.job.lower() in each.text.lower():
                        yield self._parse_detail(each.get('href').split('?')[0])
                    else:
                        control = False
            params['curPage'] += 1

    def _parse_city(self):
        index_url = 'https://www.liepin.com/citylist/'
        resp = self.request('get', index_url)
        city_index = re.findall(r'href="(/\w+/)"\stitle="%s' % self.city, resp.text)
        if city_index:
            search_url = 'https://www.liepin.com' + city_index[0]
            search_resp = self.request('get', search_url)
            city_code = re.findall(r'name="dqs"\svalue="(\d+)"', search_resp.text)[0]
            return city_code

    def _parse_detail(self, detail_url):
        resp = self.request('get', detail_url)
        html = etree.HTML(resp.text)
        title = html.xpath('//div[@class="title-info"]/h1/text()')
        if not title:
            self.logger.warning('%s 解析出错' % detail_url)
            return self._parse_detail(detail_url)
        result = {
            'title': title[0],
            'company': html.xpath('//div[@class="title-info"]/h3/a/text()')[0],
            'salary': html.xpath('//p[@class="job-item-title"]/text()')[0].strip(),
            'experience': html.xpath('//div[@class="job-qualifications"]/span[2]/text()')[0],
            'education': html.xpath('//div[@class="job-qualifications"]/span[1]/text()')[0],
            'url': detail_url,
            'description': html.xpath('string(//div[contains(@class,"job-description")]/div)')
        }
        return result


# 自定义爬虫类可在这里添加
