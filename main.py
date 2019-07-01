#!/usr/bin/env python
#-*- coding:utf-8 -*-
# author:hcj
# @File    : main.py
# datetime:2019/6/19 9:27
import argparse
import multiprocessing
import Cnki_main
import Cqvip_main

class ClockProcess(multiprocessing.Process):
    def __init__(self, main):
        multiprocessing.Process.__init__(self)
        self.main=main

    def run(self):
        self.main()
def Input():
    # 参数化输入命令行
    parser = argparse.ArgumentParser(description="Spider for gourmet shops in meituan.")
    parser.add_argument('-mode', dest='mode', help='select db mode 1:Cnki 2:Cqvip 3:Wanfang 4:All default=4', default=4,type=int)
    parser.add_argument('-restart', dest='restart', help='select restart mode 1:yes 0:no', default=1,type=int)
    parser.add_argument('-title', dest='title', help='title.', default='')
    parser.add_argument('-authors', dest='authors', help='authors', default='')
    parser.add_argument('-keywords', dest='keywords', help='keywords', default='')
    parser.add_argument('-unit', dest='unit', help='unit', default='')
    parser.add_argument('-starttime', dest='starttime', help='starttime', default=1990,type=int)
    parser.add_argument('-endtime', dest='endtime', help='endtime', default=2019,type=int)
    args = parser.parse_args()
    mode=args.title
    restart=args.restart
    title = args.title
    authors = args.authors
    keywords = args.keywords
    unit = args.unit
    starttime = args.starttime
    endtime = args.endtime


if __name__ == '__main__':
    ClockProcess(Cnki_main.ProcessMain).start()
    ClockProcess(Cqvip_main.ProcessMain).start()
    # Cnki_main.ProcessMain()