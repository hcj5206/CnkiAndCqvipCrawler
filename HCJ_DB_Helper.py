# encoding:utf-8
# name:mod_db.py
'''
使用方法：1.在主程序中先实例化DB Mysql数据库操作类。
      2.使用方法:db=database()  db.fetch_all("sql")
'''
import time
import pymysql as MySQLdb


from DBUtils.PooledDB import PooledDB
DBNAME = "cqvipcrawler"
DBHOST = "127.0.0.1"
DBUSER = "root"
DBPWD = "12345678"
DBCHARSET = "utf8"
DBPORT = 3306


class HCJ_MySQL:
    pool = None
    limit_count = 20  # 最低预启动数据库连接数量

    def __init__(self,log=None,dbname=None,dbhost=None):
        if dbname is None:
            self._dbname = DBNAME
        else:
            self._dbname = dbname
        if dbhost is None:
            self._dbhost = DBHOST
        else:
            self._dbhost = dbhost

        self._dbuser = DBUSER
        self._dbpassword = DBPWD
        self._dbcharset = DBCHARSET
        self._dbport = int(DBPORT)
        self._logger = log
        self.is_connect_first = False
        try:
            self.pool = PooledDB(MySQLdb, self.limit_count, host=self._dbhost, user=self._dbuser, passwd=self._dbpassword, db=self._dbname,
                             port=self._dbport, charset=self._dbcharset, use_unicode=True)
        except:
            if self._logger != None:
                self._logger.warn("无法连接数据库")
            else:
                print("无法连接数据库")
            self.is_connect_first=True
    def ping(self):
        print(self.pool)

    def do_sql(self, sql):
        res = ''
        try:
            conn = self.pool.connection()
            cursor = conn.cursor()
            cursor.execute(sql)
            res = cursor.fetchall()
            cursor.close()
            conn.close()
        except Exception as data:
            res=False
            if data[0] == 2006:  # 掉线
                return res
            if self._logger!=None:
                self._logger.debug("query database exception,sql= %s,%s" % (sql, data))
                self._logger.warn("query database exception %s" % (data))
            else:
                print("query database exception,sql= %s,%s" % (sql, data))
        return res
    def do_sql_one(self, sql):
        res = ''
        try:
            conn = self.pool.connection()
            cursor = conn.cursor()
            cursor.execute(sql)
            res = cursor.fetchone()
            cursor.close()
            conn.close()
        except Exception as data:
            res=False
            if data[0] == 2006:  # 掉线
                return res
            if self._logger!=None:
                self._logger.debug("query database exception,sql= %s,%s" % (sql, data))
                self._logger.warn("query database exception %s" % ( data))
            else:
                print("query database exception,sql= %s,%s" % (sql, data))
        return res
    def upda_sql(self, sql):
        res = True
        try:
            conn = self.pool.connection()
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as data:
            res = False
            if data[0]==2006: #掉线
                return res

            if self._logger!=None:
                self._logger.debug("query database exception,sql= %s,%s" % (sql, data))
                self._logger.warn("query database exception %s" % (data))
            else:
                print("query database exception,sql= %s,%s" % (sql, data))
        return res

    def insert(self,sql):
        conn = self.pool.connection()
        cursor = conn.cursor()
        try:
            cursor.execute(sql)
            conn.commit()
            return {'result': True, 'id': int(cursor.lastrowid)}
        except Exception as err:
            conn.rollback()
            return {'result': False, 'err': err}
        finally:
            cursor.close()
            conn.close()

if __name__ == '__main__':
    db=HCJ_MySQL()
    sql_count_all = "select count(*) from `databuff` where 1"
    num_all = int(db.do_sql_one(sql_count_all)[0])
    sql_count_done = "select count(*) from `databuff` where `State`=20"
    num_done = int(db.do_sql_one(sql_count_done)[0])
    print("目前有%s条数据，其中已处理的有%s，处理完成度为%.2f"%(num_all,num_done,1))