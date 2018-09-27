#!/usr/bin/env python
# -*- coding: utf-8 -*-

MYSQL_URL = 'mysql+mysqldb://root@localhost:3306/job_web?charset=utf8'

# 去重所用的Redis
HOST = 'localhost'
PORT = 6379
KEY_NAME = 'job'

UA = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;'
                  'q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/64.0.3282.119 Safari/537.36',
        'Upgrade-Insecure-Requests': '1'
}

LOGGING_CONF = {'version': 1,
                'disable_existing_loggers': False,
                'formatters': {'fh_format': {'format': '%(asctime)s [%(levelname)s] %(message)s'},
                               'sh_format': {'format': '%(asctime)s [%(levelname)s] %(message)s',
                                             'datefmt': '%H:%M:%S'
                                             }
                               },
                'handlers': {'fh': {'level': 'DEBUG',
                                    'formatter': 'fh_format',
                                    'class': 'logging.FileHandler',
                                    'filename': './log.txt'
                                    },
                             'sh': {'level': 'INFO',
                                    'formatter': 'sh_format',
                                    'class': 'logging.StreamHandler'
                                    }
                             },
                'loggers': {'root': {'handlers': ['fh', 'sh'],
                                     'level': 'DEBUG',
                                     'encoding': 'utf8'
                                     }
                            }
                }