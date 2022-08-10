"""
连接主机：rm-j6cnmk10t8b7te19j3o.mysql.rds.aliyuncs.com

prd只读：数据库：cy_prd 账号：cy_prd_read 密码：Cy123456

pre和test： 数据库：cy_pre 账号：cy_pre 密码：Cy123456

test测试：数据库：cy_test 账号：cy_test 密码：Cy123456
"""
import pymysql
from Mylog.mylog import LoggerHandler


class BaseDb:
    def __init__(self):
        self.db = DbConncet()
        self.log = LoggerHandler()
        self.account_table = 'account'

    def db_insert(self, sql):
        try:
            self.db.cursor.execute(sql)
            self.db.conn.commit()
            flag = True
        except Exception as err:
            flag = False
            self.db.conn.rollback()
            self.log.error("执行失败, %s" % err)
            self.log.error(sql)
            raise ("insert error")
        return flag

    def db_update(self, sql):
        try:
            self.db.cursor.execute(sql)
            self.db.conn.commit()
            flag = True
        except Exception as err:
            flag = False
            self.db.conn.rollback()
            self.log.error("执行失败, %s" % err)
            self.log.error(sql)
            raise ("update error")
        return flag

    def db_query(self, sql):
        try:
            self.db.cursor.execute(sql)
            res = self.db.cursor.fetchall()
        except Exception as e:
            res = False
            self.log.error('查询失败。 %s' % e)
            raise ("query error")
        return res

    def db_query_one(self, sql):
        try:
            self.db.cursor.execute(sql)
            res = self.db.cursor.fetchone()
            return res
        except Exception as e:
            res = False
            self.log.error('查询失败。 %s' % e)
        return res

    def __del__(self):
        try:
            self.db.cursor.close()
            self.db.conn.close()
        except:
            raise ("关闭数据库连接异常异常")


class DbConncet(object):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self):
        try:
            print('创建DB111')
            host = 'rm-j6cnmk10t8b7te19j3o.mysql.rds.aliyuncs.com'
            user = 'cy_test'
            passwd = 'Cy123456'
            db = 'cy_test'
            port = 3306
            self.conn = pymysql.connect(host=host, user=user, passwd=passwd, db=db, port=port, charset='utf8')
        except pymysql.Error as e:
            errormsg = 'Cannot connect to server： %s' % e
            print(errormsg)
            # exit(2)
        print('db conn ok')
        self.cursor = self.conn.cursor()
        print('db cursor ok')


# db = BaseDb()


if __name__ == '__main__':
    db = BaseDb()
    sql = """ select api_key, secret_key, passphrase, status, flag from %s where status='free'""" % 'account'
    res = db.db_query(sql)
    print(res)