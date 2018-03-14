#!/usr/bin/env python
# -*- coding: utf-8 -*-

from job_spider.process import SpiderProcess, WriterProcess
from multiprocessing import Queue
import time


def main():
    queue = Queue()
    p = {SpiderProcess: SpiderProcess(queue),
         WriterProcess: WriterProcess(queue)}
    while True:
        for i in p.keys():
            if not p[i].is_alive():
                p[i] = i(queue)
                p[i].start()
        time.sleep(1)


if __name__ == '__main__':
    main()
