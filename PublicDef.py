#!/usr/bin/env python
#-*- coding:utf-8 -*-
# author:hcj
# @File    : PublicDef.py
# datetime:2019/6/27 19:59
import re


def CreatUrlBuffTable(db,TableName):
    CreatDBTableSql = '\
            CREATE TABLE IF NOT EXISTS `%s` (\
	        `Url` VARCHAR(200) NULL DEFAULT NULL,\
	        `State` INT(11) NULL DEFAULT \'0\'  COMMENT \'-5 日期不对 -10 出现错误 0 初始 10 处理中 20 处理结束\',\
	        `Datetime` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,\
	        UNIQUE INDEX `PageIndex` (`PageIndex`)\
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8; ' % TableName
    dict_result = db.upda_sql(CreatDBTableSql)
    if not dict_result:
        print("创建出现问题")

def CreatResultDBTable(db,TableName):
    '''
    创建结构数据库表单，如果不存在就创建
    :return:
    '''
    CreatDBTableSql = '\
        CREATE TABLE IF NOT EXISTS `%s` (\
          `id` int(11) unsigned NOT NULL AUTO_INCREMENT,\
          `url` varchar(200) DEFAULT NULL, \
          `title` varchar(200) DEFAULT NULL,\
          `authors` varchar(200) DEFAULT NULL,\
          `unit` varchar(200) DEFAULT NULL,\
          `publication` varchar(200) DEFAULT NULL,\
          `keywords` varchar(200) DEFAULT NULL,\
          `abstract` text DEFAULT NULL,\
          `year` varchar(200) DEFAULT NULL,\
          `volume` varchar(200) DEFAULT NULL,\
          `issue` varchar(200) DEFAULT NULL,\
          `pagecode` varchar(200) DEFAULT NULL,\
          `doi` varchar(200) DEFAULT NULL,\
          `sponser` varchar(200) DEFAULT NULL,\
          `type` varchar(200) DEFAULT NULL,\
          PRIMARY KEY (`id`)\
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8; ' % TableName
    dict_result = db.upda_sql(CreatDBTableSql)
    if not dict_result:
        print("创建出现问题")
def RemoveSpecialCharacter(str1):
    # 去除特殊符号
    cop = re.compile(r"[^\u4e00-\u9fa5^.^a-z^A-Z^0-9]")
    string1 = cop.sub('', str(str1))  # 将string1中匹配到的字符替换成空字符
    return string1
def InsetDbbyDict(table,Dict,db):
    COLstr = ''  # 列的字段
    ROWstr = ''  # 行字段
    SearchDbname=""
    for key in list(Dict.keys()):
        Dict[key]=Dict[key].replace('\n','').replace('\"',"#").replace('\t',"").replace('\r',"").replace('\xa0',"").replace('%', ">").replace('\'', "^")
    for key in Dict.keys():
        COLstr = COLstr + ' ' + '`' + key + '`,'
        ROWstr = (ROWstr + '"%s"' + ',') % str(Dict[key])
    if  'cqvip' in Dict['url']:
        SearchDbname="cqvip"
    if  'cnki' in Dict['url']:
        SearchDbname="cnki"
    if  'wanfang' in Dict['url']:
        SearchDbname="wanfang"
    sql = "INSERT INTO %s (%s,`source`) VALUES (%s,'%s');" % (
        table,COLstr[:-1], ROWstr[:-1],SearchDbname)
    sql_select="select count(*) from `result` where `title`='%s' and `publication` LIKE '%%%%%s%%%%'"%((Dict['title']),((Dict['publication'])))
    sql_update="Update `databuff` set `State`=20 where `Url`='%s' "%str(Dict['url']).replace('>', "%")

    result_count=db.do_sql_one(sql_select)
    print(result_count)
    if  result_count[0]==0 or result_count[0]=='0':
        result_dic=db.insert(sql)

        if  result_dic['result']:#shantui
            db.upda_sql(sql_update)
        else:
            print(result_dic['err'])
            db.upda_sql("Update `databuff` set `State`=-10 where `Url`='%s' "%str(Dict['url']))
    else:
        str1=""
        for key in list(Dict.keys()):
            if str(Dict[key]) != "":
                col = key
                row = Dict[key]
                str1 = str1 + "`%s`=(case when `%s`='' then '%s' else `%s` end )," % (col, col, row, col)
        sql_update1 = "update `result` set `url`=concat(`url`,';%s'),`source`=concat(`source`,';%s'),%s where `title`='%s' and `publication` LIKE '%%%%%s%%%%'" % (Dict['url'], SearchDbname,str1[:-1], ((Dict['title'])), ((Dict['publication'])))
        db.upda_sql(sql_update1)
        sql_update = "Update `databuff` set `State`=20 where `Url`='%s' " % str(Dict['url']).replace('>', "%")
        db.upda_sql(sql_update)