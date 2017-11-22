import datetime
from qrmobservium.common import logger
from qrmobservium.persistent import dbutil
import simplejson
import rrdtool
LOG = logger.Logger(__name__)


class DeviceReader(object):

    @classmethod
    def get_device_host_by_id(cls, device_id):
        result = {}
        with dbutil.Session() as db:
            ret = db.row(sql="SELECT * FROM devices WHERE `device_id` =  %s", param=(device_id))
            print ret
            if ret is None:
                LOG.warning('id not found')
                raise KeyError('id not found')
            result['hostname'] =  ret['hostname']
        return result

    @classmethod
    def get_device_id_by_host(cls, host):
        result = {}
        with dbutil.Session() as db:
            ret = db.row(sql="SELECT * FROM devices WHERE `hostname` =  %s", param=(host))
            #print ret
            if ret is None:
                LOG.warning('id not found')
                raise KeyError('id not found')
            #for dev in ret:
            result['device_id'] =  ret['device_id']
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

    #@classmethod
    #def get_device_detail_by_id(cls, device_id):
        

class DataAnalysisReader(object):
    @classmethod
    def get_snmp_health_history_data(cls, device_id, table, sensor_id, start_time=None, end_time=None):
        result = {}
        datas = []
        tables = ['processors', 'mempools', 'printersupplies', 'sensors', 'storage']
        if table not in tables:
            LOG.warning('illegal table')
            raise KeyError('illegal table')
        dev_id = DeviceReader().get_device_host_by_id(device_id)
        
        with dbutil.Session() as db:
            #SELECT * FROM `sensors` WHERE `device_id` = '15' AND 'sensor_id' = '61'
            #SELECT * FROM `sensors` WHERE `sensor_id` = '61' AND `device_id` = '15'
            ret = db.row(sql="SELECT * FROM " + table + " WHERE `device_id` =  %s AND `sensor_id` = %s", param=(device_id, sensor_id))
            #print ret
            if ret is None:
                LOG.warning('id not found')
                raise KeyError('id not found')
            # query rrd
            rrdfile = '/opt/observium/rrd' + '/'+ dev_id['hostname'] + '/' + 'sensor' + '-' +ret['sensor_class'] + '-' + ret['sensor_type'] + '-' + ret['sensor_index'] + '.rrd'
            if start_time is None and end_time is None:
                ret = rrdtool.fetch(str(rrdfile), "AVERAGE")
            else:
                ret = rrdtool.fetch(str(rrdfile), 'AVERAGE', '-s %s' % start_time, '-e %s' % end_time)
            print ret
            timestamp = ret[0][0]
            count = 0
            for value in ret[2]:
               data = {}
               timestamp = ret[0][0] + ret[0][2] * count
               if value[0] is None:
                   data['%s' % timestamp] = value[0]
               else:
                   data['%s' % timestamp] = "%.2f" % value[0]
               count += 1
               datas.append(data)
            result['datas'] = datas
            result['unit'] = 'RPM'
            result['lower_bound'] = 'na'
            result['upper_bound'] = 'na'
            #print ret
            #print dev_id 
        #with dbutil.Session() as db:
        #    result = db.all(sql=sql, param=(device_id, sensor_id, start_time, end_time))
        return result










#print DeviceReader().get_device_detail_by_id(15)
