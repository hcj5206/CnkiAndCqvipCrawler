#!/usr/bin/env python
#-*- coding:utf-8 -*-
# author:hcj
# @File    : PublicDef.py
# datetime:2019/6/27 19:59
import re
import sys
import time

from HCJ_Buff_Control import Read_buff, Write_buff


def CreatUrlBuffTable(db,TableName):
    CreatDBTableSql = '\
            CREATE TABLE IF NOT EXISTS `%s` (\
            `Index` int(11) unsigned NOT NULL AUTO_INCREMENT,\
            `Url` VARCHAR(255) DEFAULT NULL,\
            `State` INT(11) NULL DEFAULT \'0\'  COMMENT \'-5 日期不对 -10 出现错误 0 初始 10 处理中 20 处理结束\',\
            `Datetime` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,\
            `Source` VARCHAR(200) NULL DEFAULT NULL,\
            UNIQUE INDEX `Url` (`Url`),\
            PRIMARY KEY (`Index`)\
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8; ' % TableName
    dict_result = db.upda_sql(CreatDBTableSql)
    if not dict_result:
        print("创建%s表出现问题" % TableName)

def CreatResultDBTable(db,TableName):
    '''
    创建结构数据库表单，如果不存在就创建
    :return:
    '''
    CreatDBTableSql = '\
        CREATE TABLE IF NOT EXISTS `%s` (\
          `id` int(11) unsigned NOT NULL AUTO_INCREMENT,\
          `url` text DEFAULT NULL, \
          `title` varchar(200) DEFAULT NULL,\
          `authors` varchar(200) DEFAULT NULL,\
          `unit` text  DEFAULT NULL,\
          `publication` varchar(200) DEFAULT NULL,\
          `keywords` varchar(200) DEFAULT NULL,\
          `abstract` text DEFAULT NULL,\
          `year` varchar(200) DEFAULT NULL,\
          `volume` varchar(200) DEFAULT NULL,\
          `issue` varchar(200) DEFAULT NULL,\
          `pagecode` varchar(200) DEFAULT NULL,\
          `doi` varchar(200) DEFAULT NULL,\
          `sponser` text DEFAULT NULL,\
          `type` varchar(200) DEFAULT NULL,\
          `source` varchar(200) DEFAULT NULL,\
          PRIMARY KEY (`id`)\
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8; ' % TableName
    dict_result = db.upda_sql(CreatDBTableSql)
    if not dict_result:
        print("创建出现问题")
def RemoveSpecialCharacter(str1):
    # 去除特殊符号 只留汉字 数字 字母
    cop = re.compile(r"[^\u4e00-\u9fa5^.^a-z^A-Z^0-9]")
    string1 = cop.sub('', str(str1))  # 将string1中匹配到的字符替换成空字符
    return string1
def InsetDbbyDict(table,Dict,db,DbDatabuff,Dbresult):
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
    sql_select="select count(*) from `%s` where `title`='%s' and `publication` LIKE '%%%%%s%%%%'"%(Dbresult,(Dict['title']),((Dict['publication'])))
    sql_update="Update `%s` set `State`=20 where `Url`='%s' "%(DbDatabuff,str(Dict['url']).replace('>', "%"))
    result_count=db.do_sql_one(sql_select)
    if  result_count[0]==0 or result_count[0]=='0':
        result_dic=db.insert(sql)

        if  result_dic['result']:#
            db.upda_sql(sql_update)
        else:
            print(result_dic['err'])
            db.upda_sql("Update `%s` set `State`=-10 where `Url`='%s' "%(DbDatabuff,str(Dict['url'])))
    else:
        str1=""
        for key in list(Dict.keys()):
            if str(Dict[key]) != "":
                col = key
                row = Dict[key]
                str1 = str1 + "`%s`=(case when `%s`='' then '%s' else `%s` end )," % (col, col, row, col)
        sql_update1 = "update `%s` set `url`=concat(`url`,';%s'),`source`=concat(`source`,';%s'),%s where `title`='%s' and `publication` LIKE '%%%%%s%%%%'" % (Dbresult,Dict['url'], SearchDbname,str1[:-1], ((Dict['title'])), ((Dict['publication'])))
        db.upda_sql(sql_update1)
        sql_update = "Update `%s` set `State`=20 where `Url`='%s' " % (DbDatabuff,str(Dict['url']).replace('>', "%"))
        db.upda_sql(sql_update)
def ShowStatePro(db,SearchDBName,DbDatabuff,Dbresult):
    sql_count_all = "select count(*) from `%s` where `Source`='%s'"%(DbDatabuff,SearchDBName)
    num_all = int(db.do_sql_one(sql_count_all)[0])
    sql_count_done = "select count(*) from `%s` where `State`=20 and `Source`='%s'"%(DbDatabuff,SearchDBName)
    num_done = int(db.do_sql_one(sql_count_done)[0])
    sql_count_error = "select count(*) from `%s` where `State`=-15 and `Source`='%s'"%(DbDatabuff,SearchDBName)
    num_error = int(db.do_sql_one(sql_count_error)[0])
    num_error = num_error if num_error > 0 else 0
    sql_count_done_not_in_year = "select count(*) from `%s` where `State`=-5 and `Source`='%s'"%(DbDatabuff,SearchDBName)
    num_done_not_in_year = int(db.do_sql_one(sql_count_done_not_in_year)[0])
    num_done_not_in_year = num_done_not_in_year if num_done_not_in_year > 0 else 0
    num_done = num_done + num_done_not_in_year+num_error
    if num_all > 0:
        print(
            "%s采集器：#############################################目前有%s条数据，其中已处理的有%s，其中年份不符合的有%s,无效链接%s,处理完成度为%.2f,##############################" % (
                SearchDBName,num_all, num_done, num_done_not_in_year,num_error, (int(num_done) / int(num_all)) * 100))
    if '1' in str(Read_buff(file_buff="Config.ini", settion=SearchDBName, info='flag_get_all_url')) and num_all == num_done:
        # 完成全部
        Write_buff(file_buff="Config.ini", settion=SearchDBName, info="stopflag", state=1)
        time.sleep(5)
        print("%s：爬取结束"%SearchDBName)
        sys.exit()


common_used_numerals_tmp = {'零': 0, '一': 1, '二': 2, '两': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
                            '十': 10, '百': 100, '千': 1000, '万': 10000, '亿': 100000000}
common_used_numerals = {}
for key in common_used_numerals_tmp:
    common_used_numerals[key] = common_used_numerals_tmp[key]


def chinese2digits(uchars_chinese):
    total = 0
    r = 1  # 表示单位：个十百千...
    for i in range(len(uchars_chinese) - 1, -1, -1):
        val = common_used_numerals.get(uchars_chinese[i])
        if val >= 10 and i == 0:  # 应对 十三 十四 十*之类
            if val > r:
                r = val
                total = total + val
            else:
                r = r * val
                # total =total + r * x
        elif val >= 10:
            if val > r:
                r = val
            else:
                r = r * val
        else:
            total = total + r * val
    return total


num_str_start_symbol = ['一', '二', '两', '三', '四', '五', '六', '七', '八', '九',
                        '十']
more_num_str_symbol = ['零', '一', '二', '两', '三', '四', '五', '六', '七', '八', '九', '十', '百', '千', '万', '亿']

def changeChineseNumToArab(oriStr):
    lenStr = len(oriStr)
    aProStr = ''
    if lenStr == 0:
        return aProStr
    hasNumStart = False
    numberStr = ''
    for idx in range(lenStr):
        if oriStr[idx] in num_str_start_symbol:
            if not hasNumStart:
                hasNumStart = True
            numberStr += oriStr[idx]
        else:
            if hasNumStart:
                if oriStr[idx] in more_num_str_symbol:
                    numberStr += oriStr[idx]
                    continue
                else:
                    numResult = str(chinese2digits(numberStr))
                    numberStr = ''
                    hasNumStart = False
                    aProStr += numResult
            aProStr += oriStr[idx]
            pass
    if len(numberStr) > 0:
        resultNum = chinese2digits(numberStr)
        aProStr += str(resultNum)
    return aProStr
if __name__ == '__main__':
    print(changeChineseNumToArab("第二十四期"))