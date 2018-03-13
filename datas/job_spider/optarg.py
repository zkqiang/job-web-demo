#!/usr/bin/env python
# -*- coding: utf-8 -*-

from getopt import getopt, GetoptError
import sys


class Arg(object):
    """处理命令行参数"""

    def __init__(self):
        self.help_info = '命令行用法: run.py -j 职业 -c 城市 ; 也可以直接运行 run.py'
        self.args = self._get_opt()

    def _get_opt(self):
        try:
            opts, _ = getopt(sys.argv[1:], 'hj:c:', ['help'])
            options = dict(opts)

            if len(options) == 1 and ('-h' in options or '--help' in options):
                print(self.help_info)
                exit()
            return options

        except GetoptError:
            print('参数错误')
            print(self.help_info)
            exit()

    def get_arg(self, key):
        """如果没有指定参数，则提示输入"""
        value = self.args.get(key)
        if value is None:
            if key == '-j':
                value = input('请输入职业：')
            if key == '-c':
                value = input('请输入城市：')
        return value
