#!/usr/bin/env python
#-*- coding:utf-8 -*-
# author:hcj
# @File    : main.py
# datetime:2019/6/19 9:27
import argparse
import multiprocessing
import Cnki_main
import Cqvip_main
import Wanfang_main
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
    parser.add_argument('-mode -m' , dest='mode', help='select search mode 1:Cnki 2:Cqvip 3:Wanfang 123:All default=123', default='123',type=str)
    parser.add_argument('-restart -r', dest='restart', help='select restart mode 1:yes 0:no', default=0,type=int)
    parser.add_argument('-title -t', dest='title', help='title.', default='')
    parser.add_argument('-authors -a', dest='authors', help='authors', default='')
    parser.add_argument('-keywords -k', dest='keywords', help='keywords', default='')
    parser.add_argument('-unit -u', dest='unit', help='unit', default='')
    parser.add_argument('-starttime -s', dest='starttime', help='starttime', default=1990,type=int)
    parser.add_argument('-endtime -e', dest='endtime', help='endtime', default=2019,type=int)
    parser.add_argument('-dbname -db', dest='ex_dbname', help='数据库后缀,默认为空，填xx,则表单为result', default='',type=str)
    args = parser.parse_args()
    InputDic=props(args)
    if  not InputDic['restart']==0:
        WriteIntoINI(InputDic)
def WriteIntoINI(InputDic):
    for num in range(1, 4):
        if str(num) in InputDic['mode']:
            SearchDBName = DB_List[num]
            print(SearchDBName)
            WriteInto(InputDic,SearchDBName)
def WriteInto(InputDic,SearchDBName):
    Write_buff(file_buff=".\Config.ini", settion=SearchDBName, info="restart", state=InputDic['restart'])
    Write_buff(file_buff=".\Config.ini", settion=SearchDBName, info="title", state=InputDic['title'])
    Write_buff(file_buff=".\Config.ini", settion=SearchDBName, info="authors", state=InputDic['authors'])
    Write_buff(file_buff=".\Config.ini", settion=SearchDBName, info="keywords", state=InputDic['keywords'])
    Write_buff(file_buff=".\Config.ini", settion=SearchDBName, info="unit", state=InputDic['unit'])
    Write_buff(file_buff=".\Config.ini", settion=SearchDBName, info="endtime", state=InputDic['endtime'])
    Write_buff(file_buff=".\Config.ini", settion=SearchDBName, info="starttime", state=InputDic['starttime'])
    Write_buff(file_buff=".\Config.ini", settion=SearchDBName, info="ex_dbname", state=InputDic['ex_dbname'])
def props(obj):
    pr = {}
    for name in dir(obj):
        value = getattr(obj, name)
        if not name.startswith('__') and not callable(value) and not name.startswith('_'):
            pr[name] = value
    return pr
if __name__ == '__main__':
    Input()
    ClockProcess(Cnki_main.ProcessMain).start()
    ClockProcess(Cqvip_main.ProcessMain).start()
    # ClockProcess(Wanfang_main.ProcessMain).start()
