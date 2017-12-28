import datetime
from qrmobservium.common import logger
from qrmobservium.persistent import dbutil
import simplejson
import rrdtool, re, os
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
    def get_device_by_id(cls, device_id):
        result = {}
        with dbutil.Session() as db:
            ret = db.row(sql="SELECT * FROM devices WHERE `device_id` =  %s", param=(device_id))
            #print ret
            if ret is None:
                LOG.warning('id not found')
                raise KeyError('id not found')
            #for dev in ret:
            result['device_id'] =  ret['device_id']
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

    @classmethod
    def get_devices_detail(cls):
        result = {}
        with dbutil.Session() as db:
            sql = "SELECT * FROM `devices` LEFT JOIN `devices_locations` USING (`device_id`) WHERE 1 \
                AND (( (`devices`.`device_id` != '' AND `devices`.`device_id` IS NOT NULL))) AND `devices`.`device_id` = '11' ORDER BY `devices`.`hostname`LIMIT 0,100"
            rets = db.all(sql);
            device = []
            for devices in rets:
                field = {}
                fields = {}
                for dev in devices:
                    if dev == 'last_discovered' or dev == 'last_polled' or dev == 'last_alerter' or dev == 'location_updated':
                        field[dev] = ""
                    else:
                        field[dev] = devices[dev]
                fields['device'] = field
                device.append(fields)
            result['devices'] = device
        return result
    @classmethod
    def get_device_networkinfo(cls, device_id):
        result = {}
        with dbutil.Session() as db:
            #SELECT *, `ports`.`port_id` as `port_id` FROM `ports` WHERE `device_id` = 15 ORDER BY `ifIndex` ASC
            ports = db.all(sql="SELECT *, `ports`.`port_id` as `port_id` FROM `ports` WHERE `device_id` =  %s ORDER BY `ifIndex` ASC",\
                              param=(device_id))
            #ret = db.all(sql= "SELECT *, `ports`.`port_id` as `port_id` FROM `ports` WHERE `device_id` = 15 ORDER BY `ifIndex` ASC")
            constructports = []
            for port in ports:
                #print port
                constructport = {}
                constructport["ifDescr"] = port["ifDescr"]
                constructport["port_id"] = port["port_id"]
                constructport["ifPhysAddress"] = port["ifPhysAddress"]
                constructport["ifDescr"] = port["ifDescr"]
                #get ipv4address
                address = db.row(sql= "SELECT * FROM `ipv4_addresses` WHERE `port_id` = %s", param=(port["port_id"]))
                if address:
                    constructport["ipv4_address"] = address["ipv4_address"]
                else:
                    constructport["ipv4_address"] = ""
                constructports.append(constructport)

            ipv4addresses = db.all(sql="SELECT * FROM `ipv4_addresses` AS A LEFT JOIN `ports` AS I ON I.`port_id` = A.`port_id` \
                                         LEFT JOIN `devices` AS D ON I.`device_id` = D.`device_id` \
                                         LEFT JOIN `ipv4_networks` AS N ON N.`ipv4_network_id` = A.`ipv4_network_id` \
                                         WHERE 1 AND `I`.`device_id` = %s AND ((`I`.`deleted`='0' AND (`I`.`port_id` != '' \
                                         AND `I`.`port_id` IS NOT NULL))) ORDER BY A.`ipv4_address`", param=(device_id))
            constructaddresses = []
            for address in ipv4addresses:
                constructaddress= {}
                constructaddress["ifDescr"] = address["ifDescr"]
                constructaddress["port_id"] = address["port_id"]
                constructaddress["ipv4_address"] = address["ipv4_address"]
                constructaddress["ifPhysAddress"] = address["ifPhysAddress"]
                constructaddress["ipv4_network"] = address["ipv4_network"]
                constructaddress["ipv4_prefixlen"] = address["ipv4_prefixlen"]
                constructaddress["ifAlias"] = address["ifAlias"]
                constructaddresses.append(constructaddress)
            result['device_id'] = device_id
            result['ports'] = constructports
            result['ipv4_addresses'] = constructaddresses
        return result

    @classmethod
    def get_device_arptable(cls, device_id, cur_page=1, page_size=50):
        result = {}
        with dbutil.Session() as db:
            count = db.one(sql="SELECT count('mac_id') FROM `ip_mac` AS M LEFT JOIN `ports` AS I ON I.`port_id` = M.`port_id` \
                                  WHERE 1 AND `device_id` = %s AND (((`I`.`port_id` != '' \
                                  AND `I`.`port_id` IS NOT NULL)))", param=(device_id))
            result['total'] = count
            arptable = db.all(sql="SELECT * FROM `ip_mac` AS M LEFT JOIN `ports` AS I ON I.`port_id` = M.`port_id` WHERE 1 AND `device_id` = %s \
                   AND (((`I`.`port_id` != '' AND `I`.`port_id` IS NOT NULL))) LIMIT %s,%s", param=(device_id, (cur_page-1)*page_size, page_size))
            #print len(arptable)
            metrics = []
            for ret in arptable:
                metric = {}
                metric["ip_address"] = ret["ip_address"]
                metric["port_id"] = ret["port_id"]
                metric["ifPhysAddress"] = ret["ifPhysAddress"]
                metric["ifDescr"] = ret["ifDescr"]
                metrics.append(metric)
            result['arptable'] = metrics
            result['device_id'] = device_id
        return result

    @classmethod
    def get_device_neighbours(cls, device_id):
        result = {}
        with dbutil.Session() as db:
             neighbours = db.all(sql="SELECT * FROM `neighbours` LEFT JOIN `ports` USING(`port_id`) WHERE `active` = 1 \
                       AND `device_id` = %s AND ((`deleted`='0' AND (`port_id` != '' AND `port_id` IS NOT NULL)))",  param=(device_id))
             metrics = []
             for ret in neighbours:
                 metric = {}
                 metric["port_id"] = ret["port_id"]
                 metric["ifDescr"] = ret["ifDescr"]
                 metric["ifAlias"] = ret["ifAlias"]
                 metric["remote_hostname"] = ret["remote_hostname"]
                 metric["remote_port"] = ret["remote_port"]
                 metric["remote_platform"] = ret["remote_platform"]
                 metric["remote_address"] = ret["remote_address"]
                 metric["protocol"] = ret["protocol"]
                 metrics.append(metric)
             result["neighbours"] = metrics
             result['device_id'] = device_id
        return result
    @classmethod
    def get_device_fdbtable(cls, device_id, cur_page=1, page_size=50):
        result = {}
        with dbutil.Session() as db:
            count = db.one(sql="SELECT count('vlan_id') FROM `vlans_fdb` AS F LEFT JOIN `vlans` as V ON V.`vlan_vlan` = F.`vlan_id` \
                           AND V.`device_id` = F.`device_id` LEFT JOIN `ports` AS I ON I.`port_id` = F.`port_id` WHERE 1 \
                           AND `I`.`device_id` = %s AND ((`I`.`deleted`='0' AND (`I`.`port_id` != '' AND `I`.`port_id` IS NOT NULL)))", \
                           param=(device_id))
            result['total'] = count

            fdb = db.all(sql="SELECT * FROM `vlans_fdb` AS F LEFT JOIN `vlans` as V ON V.`vlan_vlan` = F.`vlan_id` \
                           AND V.`device_id` = F.`device_id` LEFT JOIN `ports` AS I ON I.`port_id` = F.`port_id` WHERE 1 \
                           AND `I`.`device_id` = %s AND ((`I`.`deleted`='0' AND (`I`.`port_id` != '' AND `I`.`port_id` IS NOT NULL))) \
                           LIMIT %s,%s", param=(device_id, (cur_page-1)*page_size, page_size))
            metrics = []
            for ret in fdb:
                metric = {}
                metric["fdb_status"] = ret["fdb_status"]
                metric["ifName"] = ret["ifName"]
                metric["ifPhysAddress"] = ret["ifPhysAddress"]
                metric["vlan_name"] = ret["vlan_name"]
                metric["ifVlan"] = ret["ifVlan"]
                metrics.append(metric)
            result['fdbtable'] = metrics
            result['device_id'] = device_id
        return result
    @classmethod
    def get_device_vlans(cls, device_id):
        result = {}
        with dbutil.Session() as db:
            vlans = db.all(sql="SELECT * FROM `vlans` WHERE `device_id` = %s ORDER BY 'vlan_vlan'", param=(device_id))
            metrics = []

            for vlan in vlans:
                metric = {}
                constructotherports = []
                otherports = db.all(sql="SELECT * FROM `ports_vlans` AS V, `ports` as P WHERE V.`device_id` = %s AND V.`vlan` = %s \
                     AND P.port_id = V.port_id", param=(device_id, vlan['vlan_vlan']))
                for otherport in otherports:
                    constructotherport = {}
                    constructotherport["ifName"] = otherport["ifName"]
                    constructotherport["ifIndex"] = otherport["ifIndex"]
                    constructotherports.append(constructotherport)
                ports = db.all(sql="SELECT * FROM ports WHERE `device_id` = %s AND `ifVlan` = %s", param=(device_id, vlan['vlan_vlan']))
                for port in ports:
                    for ports_vlan in constructotherports:
                        if port['ifIndex'] == ports_vlan["ifIndex"]:
                            ports_vlan["untagged"] = 1
                metric["vlan_vlan"] = vlan["vlan_vlan"]
                metric["vlan_name"] = vlan["vlan_name"]
                metric["otherports"] = constructotherports
                metrics.append(metric)
            result['vlan'] = metrics
        return result


class DataAnalysisReader(object):

    @classmethod
    def get_snmp_health_history_data(cls, device_id, table, metric_id, start_time=None, end_time=None):
        result = {}
        datas = []
        columns = []
        #tables = ['processors', 'mempools', 'printersupplies', 'sensors', 'storage']
        tables = {'processors': 'processor', 'mempools': 'mempool', 'printersupplies': 'supply', 'sensors': 'sensor', 'storage': 'storage', \
                  'ports':'port'}
        if any( curtable == table  for curtable in tables) is False:
            LOG.warning('illegal table')
            raise KeyError('illegal table')
        dev_id = DeviceReader().get_device_host_by_id(device_id)
        
        with dbutil.Session() as db:
            #SELECT * FROM `sensors` WHERE `sensor_id` = '61' AND `device_id` = '15'

            ret = db.row(sql="SELECT * FROM " + table + " WHERE `device_id` =  %s AND " + tables[table] + "_id" + "= %s", param=(device_id, metric_id))
            if ret is None:
                LOG.warning('id not found')
                raise KeyError('id not found')
            # query rrd
            rrdfile = ''
            if tables[table] == 'sensor':
                rrdfile = '/opt/observium/rrd' + '/'+ dev_id['hostname'] + '/' + tables[table] + \
                           '-' + ret['sensor_class'] + '-' + ret['sensor_type'] + '-' + ret['sensor_index'] + '.rrd'
                #for sensor, the unit should be sensor_class
            elif tables[table] == 'mempool':
                rrdfile = '/opt/observium/rrd' + '/' + dev_id['hostname'] + '/' + tables[table] + \
                           '-' + ret['%s_mib' %  tables[table]].lower() + '-' + ret['%s_index' % tables[table]] + '.rrd'
                result['unit'] = 'Bytes'
            elif tables[table] == 'storage':
               filename = ret['%s_mib' % tables[table]].lower() + '-' + ret['%s_descr' % tables[table]]
               filename = re.sub('[^a-zA-Z0-9,._\-]', '_', filename)
               rrdfile = '/opt/observium/rrd' + '/' + dev_id['hostname'] + '/' + tables[table] + \
                         '-' + filename + '.rrd'
               result['unit'] = 'Bytes'
            elif tables[table] == 'processor':
               #Reference includes/polling/processors.inc.php line 50
               rrdfile = '/opt/observium/rrd' + '/' + dev_id['hostname'] + '/' + tables[table] + \
                           '-' + ret['%s_type' % tables[table]] + '-' + ret['%s_index' % tables[table]] + '.rrd'
            elif tables[table] == 'port':
               rrdfile = '/opt/observium/rrd' + '/' + dev_id['hostname'] + '/' + tables[table] + \
                            '-' + str(ret['ifIndex']) + '.rrd'
            #print rrdfile
            if not os.path.exists(rrdfile):
                LOG.warning('rrdfile not found')
                raise KeyError('rrdfile not found')
            if start_time is None and end_time is None:
                ret = rrdtool.fetch(str(rrdfile), "AVERAGE")
            else:
                ret = rrdtool.fetch(str(rrdfile), 'AVERAGE', '-s %s' % start_time, '-e %s' % end_time)
            #print ret
            timestamp = ret[0][0]
            count = 0
            if len (ret[1]) >= 2:
                for column in ret[1]:
                    columns.append(column)
                result['columns'] = columns
            for value in ret[2]:
               data = {}
               column = {}
               timestamp = ret[0][0] + ret[0][2] * count
               if value[0] is None:
                   data['%s' % timestamp] = value[0]
               else:
                   if len(value) >= 2:
                       data['%s' % timestamp] = ["%.2f" % detailvalue for detailvalue in value]
                   else:
                       data['%s' % timestamp] = "%.2f" % value[0]
               count += 1
               datas.append(data)
            result['datas'] = datas
            result['lower_bound'] = 'na'
            result['upper_bound'] = 'na'
            #print ret
            #print dev_id 
        #with dbutil.Session() as db:
        #    result = db.all(sql=sql, param=(device_id, sensor_id, start_time, end_time))
        return result










#print DeviceReader().get_device_detail_by_id(15)
