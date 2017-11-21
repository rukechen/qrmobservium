import pymysql.cursors

from qrmobservium.common import logger
from qrmobservium.persistent.db_connector import MysqlDataSource

LOG = logger.Logger(__name__)

class Session(object):

    def __init__(self):
        LOG.debug('request db connection from pool')
        self.conn = MysqlDataSource().get_datasource().connection()
        self.cur = self.conn.cursor(pymysql.cursors.DictCursor)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            LOG.debug('return db connection to pool')
            self.cur.close()
            self.conn.close()

    def one(self, sql, param=None):
        # return None if query not found

        # apply param if value is not None and not empty array
        if param:
            self.cur.execute(sql, param)
        else:
            self.cur.execute(sql, None)
        record = self.cur.fetchone()

        # python 3
        # list(record.values())
        if record is not None and len(record.values())>0:
            return record.values()[0]
        else:
            return None

    def row(self, sql, param=None):
        # return None if query not found

        if param:
            self.cur.execute(sql, param)
        else:
            self.cur.execute(sql, None)
        return self.cur.fetchone()

    def all(self, sql, param=None):
        # return empty tuple if query not found

        if param:
            self.cur.execute(sql, param)
        else:
            self.cur.execute(sql, None)
        return self.cur.fetchall()

    def execute(self, sql, param=None):
        if param:
            result = self.cur.execute(sql, param)
        else:
            result = self.cur.execute(sql, None)
        self.conn.commit()
        return result

    def insert(self, table, param_dict):
        placeholders = ', '.join(['%s'] * len(param_dict))
        columns = ', '.join(param_dict.keys())
        sql = "INSERT INTO %s (%s) VALUES (%s)" % (table, columns, placeholders)
        LOG.debug("insert sql: %s vals:%s" % (sql, param_dict.values()) )
        return self.cur.execute(sql, param_dict.values())
