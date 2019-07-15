#!/usr/bin/env python
#-*- coding:utf-8 -*-
# author:hcj
# @File    : main.py
# datetime:2019/6/19 9:27
import argparse
import multiprocessing
import time
import lxml
from HCJ_Buff_Control import Write_buff
DB_List={
        1:"Cnki",
        2:"Cqvip",
        3:"Wanfang",
    }

class ClockProcess(multiprocessing.Process):
    def __init__(self, main):
        multiprocessing.Process.__init__(self)
        self.main=main

    def run(self):
        self.main()
def Input():
    # 参数化输入命令行
    parser = argparse.ArgumentParser(description="Spider for gourmet shops in meituan.")
    parser.add_argument('-mode -m' , dest='mode', help='选择模式：1:Cnki 2:Cqvip 3:Wanfang 12：Cnki+Cqvip 123:All 默认0', default='0',type=str)
    parser.add_argument('-restart -r', dest='restart', help='是否重新开始爬取 1 重新开始 0：继续 默认为0', default=0,type=int)
    parser.add_argument('-title -t', dest='title', help='title：标题', default='')
    parser.add_argument('-authors -a', dest='authors', help='authors：作者', default='')
    parser.add_argument('-keywords -k', dest='keywords', help='keywords：关键词', default='')
    parser.add_argument('-unit -u', dest='unit', help='unit：单位', default='')
    parser.add_argument('-starttime -s', dest='starttime', help='starttime：开始时间', default=1990,type=int)
    parser.add_argument('-endtime -e', dest='endtime', help='endtime：结束时间', default=2019,type=int)
    parser.add_argument('-dbname -db', dest='ex_dbname', help='数据库后缀,默认为空，填xx,则表单为result', default='',type=str)
    args = parser.parse_args()
    InputDic=props(args)
    if  not InputDic['restart']==0:
        WriteIntoINI(InputDic)
    return InputDic['mode']
def WriteIntoINI(InputDic):
    for num in range(1, 4):
        if str(num) in InputDic['mode']:

            SearchDBName = DB_List[num]
            print(SearchDBName)
            WriteInto(InputDic,SearchDBName)
def WriteInto(InputDic,SearchDBName):
    Write_buff(file_buff="Config.ini", settion=SearchDBName, info="restart", state=InputDic['restart'])
    Write_buff(file_buff="Config.ini", settion=SearchDBName, info="title", state=InputDic['title'])
    Write_buff(file_buff="Config.ini", settion=SearchDBName, info="authors", state=InputDic['authors'])
    Write_buff(file_buff="Config.ini", settion=SearchDBName, info="keywords", state=InputDic['keywords'])
    Write_buff(file_buff="Config.ini", settion=SearchDBName, info="unit", state=InputDic['unit'])
    Write_buff(file_buff="Config.ini", settion=SearchDBName, info="endtime", state=InputDic['endtime'])
    Write_buff(file_buff="Config.ini", settion=SearchDBName, info="starttime", state=InputDic['starttime'])
    Write_buff(file_buff="Config.ini", settion=SearchDBName, info="ex_dbname", state=InputDic['ex_dbname'])
def props(obj):
    pr = {}
    for name in dir(obj):
        value = getattr(obj, name)
        if not name.startswith('__') and not callable(value) and not name.startswith('_'):
            pr[name] = value
    return pr
if __name__ == '__main__':
    mode =Input()
    time.sleep(1)
    import Cnki_main
    import Cqvip_main
    import Wanfang_main
    if '1' in mode:
        ClockProcess(Cnki_main.ProcessMain).start()
    if '2' in mode:
        ClockProcess(Cqvip_main.ProcessMain).start()
    if '3' in mode:
        ClockProcess(Wanfang_main.ProcessMain).start()
