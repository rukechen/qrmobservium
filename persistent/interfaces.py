import datetime
from qrmobservium.common import logger
from qrmobservium.persistent import dbutil
import simplejson
LOG = logger.Logger(__name__)


class DeviceReader(object):

    @classmethod
    def get_device_id_by_host(cls, host):
        result = {}
        with dbutil.Session() as db:
            ret = db.all(sql="SELECT * FROM devices WHERE `hostname` =  %s", param=(host))
            #print ret
            if ret is None:
                LOG.warning('id not found')
                raise KeyError('id not found')
            for dev in ret:
                result['device_id'] =  dev['device_id']
        return result
        
    @classmethod
    def get_device_detail_by_id(cls, device_id):
        result = {}
        metrics = []
        tables = {'processors': 'processor', 'mempools': 'mempool', 'printersupplies': 'supply', 'sensors': 'sensor', 'storage': 'storage'}
        with dbutil.Session() as db:
            for table in tables:
                metrics_id = []
                metric = {}
                ret = db.all(sql="SELECT * FROM " + table+ " WHERE `device_id` =  %s", param=(device_id))
                if ret is None:
                    LOG.warning('id not found')
                    raise KeyError('id not found')
                for dev in ret:
                    template = {}
                    template['metric_id'] = dev['%s_id' % tables[table]]
                    template['metric_descr'] = dev['%s_descr' % tables[table]]
                
                    metrics_id.append(template)
                metric['table_name'] = table
                metric['metrics_id'] = metrics_id

                metrics.append(metric)
                result['device_id'] = device_id
                result['metrics'] = metrics
            print simplejson.dumps(result)
            
        return result


#print DeviceReader().get_device_detail_by_id(15)
