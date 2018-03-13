#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datas.job_spider.process import SpiderProcess, WriterProcess
from multiprocessing import Queue


def main():
    queue = Queue()
    p1 = SpiderProcess(queue)
    p2 = WriterProcess(queue)
    p1.start()
    p2.start()
    p1.join()
    p2.join()


if __name__ == '__main__':
    main()
