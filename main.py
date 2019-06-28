#!/usr/bin/env python
#-*- coding:utf-8 -*-
# author:hcj
# @File    : main.py
# datetime:2019/6/19 9:27
import multiprocessing
import Cnki_main
import Cqvip_main

class ClockProcess(multiprocessing.Process):
    def __init__(self, main):
        multiprocessing.Process.__init__(self)
        self.main=main

    def run(self):
        self.main()

if __name__ == '__main__':
    ClockProcess(Cnki_main.ProcessMain).start()
    ClockProcess(Cqvip_main.ProcessMain).start()
    # Cnki_main.ProcessMain()