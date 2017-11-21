import pymysql
from DBUtils.PooledDB import PooledDB
from qrmobservium.config_file import config
from qrmobservium.common import logger
from qrmobservium.common.singleton import Singleton

LOG = logger.Logger(__name__)

class MysqlDataSource(object):
    __metaclass__ = Singleton

    def __init__(self):
        LOG.info('mysql connection pool creating')
        self.dbpool = PooledDB(creator=pymysql, mincached=config.DB_MIN_CACHED , maxcached=config.DB_MAX_CACHED,
                           maxshared=config.DB_MAX_SHARED, maxconnections=config.DB_MAX_CONNECYIONS,
                           blocking=True,
                           host=config.DB_HOST , port=config.DB_PORT ,
                           db=config.DB_DBNAME , charset=config.DB_CHARSET)
        LOG.info('mysql connection pool created')

    def get_datasource(self):
        return self.dbpool
