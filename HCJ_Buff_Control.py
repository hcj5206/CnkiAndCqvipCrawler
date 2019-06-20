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
'''
cf = ConfigParser()
        cf.read("Config.ini", encoding='utf-8')
        cf.set(self.SearchName, 'maxpage', str(self.MaxPage))
        cf.write(open('Config.ini', 'w', encoding='utf-8'))'''

def Write_buff(file_buff="Config.ini", settion="Cqvip", info=None, state=None):
    config = ConfigParser.ConfigParser()
    if info == "":
        return
    if os.path.exists(file_buff):
        config.read(file_buff,encoding='utf-8')
        if not config.has_section(settion):
            config.add_section(settion)
        config.set(settion, info, str(state))
        config.write(open(file_buff, "r+", encoding='utf-8'))
    else:
        config.add_section(settion)
        config.write(open(file_buff, "w"))
        config.read(file_buff)
        config.set(settion, info, str(state))
        config.write(open(file_buff, "r+", encoding='utf-8'))

def Read_buff(file_buff="Config.ini", settion="info", info=None):
    if os.path.exists(file_buff):
        config = ConfigParser.ConfigParser()
        config.read(file_buff, encoding='utf-8')
        if config.has_option(settion, info):
            test_value = config.get(settion, info)
            return test_value
        else:
            return None
    else:
        print("Not exit %s"%file_buff)
        return None


if __name__ == '__main__':
    Write_buff(file_buff="Config.ini",settion="Cqvip",info="startpage",state=43)
    pass
