#!/usr/bin/env python
# -*- coding: utf-8 -*-
import redis

HOST = 'localhost'
PORT = 6379
KEY_NAME = 'job'


class RedisOperator(object):

    def __init__(self):
        """初始化 Redis 连接"""
        self.key = KEY_NAME
        self._conn = redis.StrictRedis(
            host=HOST, port=PORT, max_connections=20, decode_responses=True)

    def add(self, url):
        return self._conn.sadd(self.key, url)
