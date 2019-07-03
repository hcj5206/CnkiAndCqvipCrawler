#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
 time:20190426
 author: HCJ
 自写类
'''
import configparser as ConfigParser
import os
import time


def Write_buff(file_buff="Config.ini", settion="Cqvip", info=None, state=None):
    config = ConfigParser.ConfigParser()
    if info == "":
        return
    if os.path.exists(file_buff):
        try:
            config.read(file_buff,encoding='utf-8-sig')
            config.set(settion, info, str(state))
            config.write(open(file_buff, "w+", encoding='utf-8-sig'))
        except:
            print("jhha")
    else:
        pass

def Read_buff(file_buff="Config.ini", settion="info", info=None):
    if os.path.exists(file_buff):
        config = ConfigParser.ConfigParser()
        config.read(file_buff, encoding='utf-8-sig')
        if config.has_option(settion, info):
            test_value = config.get(settion, info)
            return test_value
        else:
            return ""
    else:
        print("Not exit %s"%file_buff)
        return None


if __name__ == '__main__':
    print(Read_buff(file_buff="Config.ini", settion="DB",info='DBNAME'))
    pass
