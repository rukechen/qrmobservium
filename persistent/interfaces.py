import datetime, time
from qrmobservium.common import logger
from qrmobservium.persistent import dbutil
import simplejson
import rrdtool, re, os
from collections import defaultdict
LOG = logger.Logger(__name__)


class DeviceReader(object):

    @classmethod
    def get_device_host_by_id(cls, device_id):
        result = {}
        with dbutil.Session() as db:
            ret = db.row(sql="SELECT * FROM devices WHERE `device_id` =  %s", param=(device_id))
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
    def get_devices(cls, cur_page=1, page_size=50):
        result = {}
        metrics = []
        with dbutil.Session() as db:
            count = db.one(sql="SELECT count(*) FROM `devices`")
            result['total'] = count
            devices = db.all(sql="SELECT * FROM `devices` LIMIT %s,%s", param=((cur_page-1)*page_size, page_size))
            for dev in devices:
                metric = {}
                metric['device_id'] = dev['device_id']
                metric['hostname'] = dev['hostname']
                metric['device_ip'] = dev['hostname']
                metric['os'] = dev['os']
                metric['status'] = dev['status']
                metric['mgmt_tech'] = 'SNMP'
                metrics.append(metric)
            result['datas'] = metrics
            return result

    @classmethod
    def get_device_detail_by_id(cls, device_id):
        result = {}
        metrics = []
        tables = {'processors': 'processor', 'mempools': 'mempool', 'printersupplies': 'supply', 'sensors': 'sensor', 'storage': 'storage'}
        with dbutil.Session() as db:
            ret = db.row(sql="SELECT * FROM devices WHERE `device_id` =  %s", param=(device_id))
            if ret is None:
                LOG.warning('id not found')
                raise KeyError('id not found')
            for table in tables:
                ret = db.all(sql="SELECT * FROM " + table+ " WHERE `device_id` =  %s", param=(device_id))
                mac = db.row(sql="SELECT * FROM `devices` AS M LEFT JOIN `ipv4_addresses` AS I ON I.ipv4_address = \
                 CONVERT(M.hostname USING utf8) COLLATE utf8_unicode_ci LEFT JOIN `ports` AS P ON P.port_id = I.port_id \
                                WHERE M.`device_id` = %s", param=(device_id))
                for dev in ret:
                    template = {}
                    metadata = {}
                    template['sensor_name'] = dev['%s_descr' % tables[table]]
                    metadata['metric_id'] = dev['%s_id' % tables[table]]
                    metadata['sensor_table'] = table
                    if table == 'sensors':
                        metadata['sensor_type'] = dev['%s_class' % tables[table]]
                    else:
                        metadata['sensor_type'] = table
                    template['metadata'] = metadata
                    metrics.append(template)
 
                result['ifPhysAddress'] = mac['ifPhysAddress']
                result['device_id'] = device_id
                result['sensor'] = metrics
            
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

    @classmethod
    def get_device_summary(cls):
        result = {}
        with dbutil.Session() as db:
            metric = {}
            metadata = {}
            metric["total"] = db.one(sql="SELECT count(*) FROM `devices`")
            metadata["up"] = db.one(sql="SELECT count(*) FROM `devices` WHERE status = 1 AND disabled = 0")
            metadata["down"] = db.one(sql="SELECT count(*) FROM `devices` WHERE status = 0 AND disabled = 0")
            metadata["disabled"] = db.one(sql="SELECT count(*) FROM `devices` WHERE disabled = 1 ")
            metric["metadata"] = metadata
            result["devices"] = metric

            metric = {}
            metadata = {}
            metric["total"] = db.one(sql="SELECT count(*) FROM `ports` WHERE 1 \
                            AND (( (`device_id` != '' AND `device_id` IS NOT NULL)) OR ((`port_id` != '' AND `port_id` IS NOT NULL))) \
                            AND `deleted` = 0 AND `ignore` = 0")
            metadata["shutdown"] = db.one(sql="SELECT count(*) FROM `ports` WHERE 1 \
                            AND (( (`device_id` != '' AND `device_id` IS NOT NULL)) OR ((`port_id` != '' AND `port_id` IS NOT NULL))) \
                            AND `deleted` = 0 AND `ignore` = 0 \
                            AND `ifAdminStatus` = %s", param=("down"))
            metadata["down"] = db.one(sql="SELECT count(*) FROM `ports` WHERE 1 \
                            AND (( (`device_id` != '' AND `device_id` IS NOT NULL)) OR ((`port_id` != '' AND `port_id` IS NOT NULL))) \
                            AND `deleted` = 0 AND `ignore` = 0 \
                            AND `ifAdminStatus` = %s AND `ifOperStatus` IN (%s, %s) \
                            AND `ports`.`disabled` = '0' AND `ports`.`deleted` = '0'", param=("up","down","lowerLayerDown"))
            metadata["up"] = db.one(sql="SELECT count(*) FROM `ports` WHERE 1 \
                            AND (( (`device_id` != '' AND `device_id` IS NOT NULL)) OR ((`port_id` != '' AND `port_id` IS NOT NULL))) \
                            AND `deleted` = 0 AND `ignore` = 0 \
                            AND `ifAdminStatus` = %s AND `ifOperStatus` IN (%s, %s, %s) \
                            AND `ports`.`disabled` = '0' AND `ports`.`deleted` = '0'", param=("up","up","testing", "monitoring"))
            metric["metadata"] = metadata
            result["ports"] = metric

            metric = {}
            metadata = {}
            metric["total"] = db.one(sql="SELECT count(*) FROM `sensors` WHERE 1 \
                            AND (( (`device_id` != '' AND `device_id` IS NOT NULL)) OR ((`sensor_id` != '' AND `sensor_id` IS NOT NULL))) \
                            AND `sensor_deleted` = 0 AND `sensor_ignore` = 0 ")
            metadata["ok"] = db.one(sql="SELECT count(*) FROM `sensors` WHERE 1 \
                            AND (( (`device_id` != '' AND `device_id` IS NOT NULL)) OR ((`sensor_id` != '' AND `sensor_id` IS NOT NULL))) \
                            AND `sensor_deleted` = 0 AND `sensor_ignore` = 0 AND `sensor_disable` = 0 \
                            AND `sensor_event` = %s", param=("ok"))
            metadata["down"] = db.one(sql="SELECT count(*) FROM `sensors` WHERE 1 \
                            AND (( (`device_id` != '' AND `device_id` IS NOT NULL)) OR ((`sensor_id` != '' AND `sensor_id` IS NOT NULL))) \
                            AND `sensor_deleted` = 0 AND `sensor_ignore` = 0 AND `sensor_disable` = 0 \
                            AND `sensor_event` NOT IN (%s)", param=("ok"))
            metadata["disabled"] = db.one(sql="SELECT count(*) FROM `sensors` WHERE 1 \
                            AND (( (`device_id` != '' AND `device_id` IS NOT NULL)) OR ((`sensor_id` != '' AND `sensor_id` IS NOT NULL))) \
                            AND `sensor_deleted` = 0 AND `sensor_disable` = 1")
            metric["metadata"] = metadata
            result["sensors"] = metric

            metric = {}
            metadata = {}
            metric["total"] = db.one(sql="SELECT count(*) FROM `status` WHERE 1 \
                            AND (( (`device_id` != '' AND `device_id` IS NOT NULL)) OR ((`status_id` != '' AND `status_id` IS NOT NULL))) \
                            AND `status_deleted` = 0 AND `status_ignore` = 0 ")
            metadata["ok"] = db.one(sql="SELECT count(*) FROM `status` WHERE 1 \
                            AND (( (`device_id` != '' AND `device_id` IS NOT NULL)) OR ((`status_id` != '' AND `status_id` IS NOT NULL))) \
                            AND `status_deleted` = 0 AND `status_ignore` = 0 AND `status_disable` = 0 \
                            AND `status_event` IN (%s, %s)", param=("ok", "warning"))
            metadata["alert"] = db.one(sql="SELECT count(*) FROM `status` WHERE 1 \
                            AND (( (`device_id` != '' AND `device_id` IS NOT NULL)) OR ((`status_id` != '' AND `status_id` IS NOT NULL))) \
                            AND `status_deleted` = 0 AND `status_ignore` = 0 AND `status_disable` = 0 \
                            AND `status_event` NOT IN (%s, %s)", param=("ok", "warning"))
            metadata["disabled"] = db.one(sql="SELECT count(*) FROM `status` WHERE 1 \
                            AND (( (`device_id` != '' AND `device_id` IS NOT NULL)) OR ((`status_id` != '' AND `status_id` IS NOT NULL))) \
                            AND `status_deleted` = 0 AND `status_ignore` = 0 AND `status_disable` = 1")
            metric["metadata"] = metadata
            result["status"] = metric
        return result

    @classmethod
    def get_device_available(cls):
        metrics = []
        with dbutil.Session() as db:
            devices = db.all(sql="SELECT `device_id`, `status`, `last_polled` FROM `devices`")
            for dev in devices:
                metric = {}
                if dev["status"] == 1:
                    last_polled_time = dev["last_polled"]
                    delta_time = datetime.datetime.now() - last_polled_time
                    if delta_time.total_seconds() > 600:
                        metric["status"] = 0
                    else:
                        metric["status"] = dev ["status"]
                else:
                    metric["status"] = dev ["status"]
                metric["device_id"] = dev["device_id"]
                metrics.append(metric)

        return metrics
    @classmethod
    def get_device_available_by_id(cls, device_id):
        result = {}
        with dbutil.Session() as db:
            device = db.row(sql="SELECT `device_id`, `status`, `last_polled` FROM `devices` WHERE `device_id` = %s ", param=(device_id))
            if device is None:
                LOG.warning('id not found')
                raise KeyError('id not found')
            if device["status"] == 1:
                last_polled_time = device["last_polled"]
                delta_time = datetime.datetime.now() - last_polled_time
                if delta_time.total_seconds() > 600:
                    result["status"] = 0
                else:
                    result["status"] = device ["status"]
            else:
                result["status"] = device ["status"]
            result["device_id"] = device["device_id"]

        return result
    @classmethod
    def get_device_sensors_by_id(cls, device_id):
        result = []
        tables = {'processors':'processor', 'mempools':'mempool', 'sensors':'sensor', 'status':'status', "storage":"storage", "ports":"port"}
        with dbutil.Session() as db:
            ret = db.row(sql="SELECT * FROM devices WHERE `device_id` =  %s", param=(device_id))
            if ret is None:
                LOG.warning('id not found')
                raise KeyError('id not found')
            for table in tables:
                #print tables[table]
                if table == 'sensors':
                    values = db.all(sql="SELECT " + tables[table] + "_id ," + tables[table] + "_class," + tables[table] + "_descr"\
                              + " FROM " + table + " WHERE `device_id` = %s", param=(device_id))
                elif table == 'ports':
                    values = db.all(sql="SELECT " + tables[table] + "_id ," + "ifDescr" \
                              + " FROM " + table + " WHERE `device_id` = %s", param=(device_id))
                else:
                    values = db.all(sql="SELECT " + tables[table] + "_id ," + tables[table] + "_descr" \
                              + " FROM " + table + " WHERE `device_id` = %s", param=(device_id))
                if values is None:
                    LOG.warning('id not found')
                    raise KeyError('id not found')
                for val in values:
                    metric = {}
                    if table == 'sensors':
                        metric['sensor_type'] = val['%s_class' % tables[table]]
                    else:
                        metric['sensor_type'] = 'unknown'

                    if table == 'ports':
                        metric['name'] = val['ifDescr']
                    else:
                        metric['name'] = val['%s_descr' % tables[table]]
                    metric['metric'] = table
                    metric['metric_id'] = val['%s_id' % tables[table]]
                    result.append(metric)

        return result

class AlertReader(object):
    @classmethod
    def get_alerts(cls, device_id=None, entity_type=None, alert_status=None, order_by=None):
        result = {}
        with dbutil.Session() as db:
            order_cmd = " ORDER BY "
            order_cmd = order_cmd + "last_alerted DESC"
            filter_cmd = ""
            filter_params = []
            if device_id:
                filter_cmd = filter_cmd + " and `alert_table`.device_id = %s "
                filter_params.append(device_id)
            if entity_type:
                filter_cmd = filter_cmd + " and `alert_table`.entity_type = %s "
                filter_params.append(entity_type)
            # alert_status
            filter_cmd = filter_cmd + " and `alert_status` IN (%s) "
            filter_params.append(alert_status)
            order_cmd = " ORDER BY "
            order_cmd = order_cmd + order_by + " DESC"

            sql = "SELECT `alert_table`.device_id, `alert_table`.entity_type, `alert_table`.entity_id,\
                   `alert_table`.alert_test_id as alert_setting_id, alert_status, last_checked, \
                   last_alerted, last_changed, B.alert_name,C.hostname FROM `alert_table` \
                   LEFT JOIN `alert_tests` AS B ON `alert_table`.alert_test_id = B.alert_test_id  \
                   LEFT JOIN `devices` as C on C.device_id=`alert_table`.device_id  WHERE 1 \
                   AND (( (`alert_table`.`device_id` != '' AND `alert_table`.`device_id` IS NOT NULL)))" \
                  + filter_cmd + order_cmd
            result = db.all(sql = sql, param=filter_params)
            return result


    @classmethod
    def get_alert_settings(cls, cur_page=1, page_size=2):
        result = {}
        filter_params = []
        with dbutil.Session() as db:
            csql = "SELECT COUNT(alert_tests.alert_test_id) FROM alert_tests"
            result['total'] = db.one(sql=csql)
            sql = "SELECT alert_tests.alert_test_id as alert_setting_id, alert_tests.entity_type, alert_name, alert_message,conditions FROM alert_tests LIMIT %s, %s"
            assocsql = "SELECT * FROM `alert_assoc` WHERE 1 AND alert_test_id= %s"
            devsql = "SELECT DISTINCT(device_id) FROM `alert_table` WHERE 1 AND alert_test_id= %s"
            filter_params.append((cur_page-1)*page_size)
            filter_params.append(page_size)
            alert_settings = db.all(sql=sql, param=filter_params)
            for alert_setting in alert_settings:
                alert_assocs = []
                alert_assoc = {}
                #Only support first entity_attribs
                assocs = db.row(sql=assocsql, param= alert_setting['alert_setting_id'])
                alert_assoc['alert_assoc_id'] = assocs['alert_assoc_id']
                alert_assoc['entity_attribs'] = [simplejson.loads(assocs['entity_attribs'])[0]]
                alert_assocs.append(alert_assoc)
                alert_setting['alert_assoc'] = alert_assocs

                conditions = simplejson.loads(alert_setting['conditions'])
                alert_setting['condition_metric'] = conditions[0]['metric']
                alert_setting['condition_symbol'] = conditions[0]['condition']
                alert_setting['condition_value'] = conditions[0]['value']
                del alert_setting['conditions']
                devices = db.all(sql=devsql, param= alert_setting['alert_setting_id'])
                alert_setting['devices'] = devices
            result['datas']  = alert_settings
        return result
class AlertWriter(object):
    @classmethod
    def match_device_entities(cls, db, device_id, entity_attribs, entity_type):
        translate_to_table = {'processor':'processors', 'mempool':'mempools', 'sensor':'sensors', 'status':'status', "storage":"storage", "port":"ports", 'device': 'devices'}
        filter_params = []

        if entity_type == 'storage':
            sql = "SELECT * from " + translate_to_table[entity_type] + " WHERE device_id = %s AND storage_deleted !=1"
        elif entity_type == 'port':
            sql = "SELECT * from " + translate_to_table[entity_type] + " WHERE device_id = %s AND deleted !=1"
        elif entity_type == 'mempool':
            sql = "SELECT * from " + translate_to_table[entity_type] + " WHERE device_id = %s AND mempool_deleted !=1"
        else:
            sql = "SELECT * from " + translate_to_table[entity_type] + " WHERE device_id = %s"
        filter_params.append(device_id)
        for attr in entity_attribs:
             if attr['condition'] == 'gt' or attr['condition'] == 'greater' or attr['condition'] == '>':
                 sql= sql + ' AND ' + attr['attrib'] + ' > %s'
                 filter_params.append(attr['value'])
             elif attr['condition'] == 'lt' or attr['condition'] == 'less' or attr['condition'] == '<':
                 sql= sql + ' AND ' + attr['attrib'] + ' < %s'
                 filter_params.append(attr['value'])
             elif attr['condition'] == 'equals' or attr['condition'] == 'eq' or attr['condition'] == 'is' or attr['condition'] == '==' or  attr['condition'] == '=':
                 sql= sql + ' AND ' + attr['attrib'] + ' = %s'
                 filter_params.append(attr['value'])
             elif attr['condition'] == 'in':
                 value = attr['value'].split(',')
                 sql = sql + " AND " + attr['attrib'] + " IN ('%s')" % ("','".join(str(x) for x in value))
        #print sql
        #print filter_params
        entities = db.all(sql=sql, param=filter_params)
        return entities
    @classmethod
    def getcurrent_alert_table(cls, db):
        devsql = "SELECT device_id FROM devices"
        sql = "SELECT * FROM `alert_table`"
        devices = db.all(sql=devsql)
        ret = db.all(sql=sql)
        curr_alert_table = {}
        result = {}
        for dev in devices:
            sql = "SELECT * FROM `alert_table` WHERE device_id = %s"
            ret = db.all(sql=sql, param = dev['device_id'])
            curr_alert_table = defaultdict( lambda: defaultdict(lambda: defaultdict( dict )))

            for alert_table in ret:
                curr_alert_table[alert_table['entity_type']][str(alert_table['entity_id'])][str(alert_table['alert_test_id'])] = alert_table

            result[dev['device_id']] = curr_alert_table
        return result
    @classmethod
    def match_device(cls, db, dev_id, device_attribs):
        ret = False
        #print device_attribs
        filter_params = []
        devcsql = "SELECT COUNT(*) FROM `devices` AS d  WHERE d.`device_id` = %s"
        filter_params.append(int(dev_id))
        for attr in device_attribs:
            if attr['condition'] == 'gt' or attr['condition'] == 'greater' or attr['condition'] == '>':
                devcsql= devcsql + ' AND `d`.' + attr['attrib'] + ' > %s'
                filter_params.append(attr['value'])
            elif attr['condition'] == 'lt' or attr['condition'] == 'less' or attr['condition'] == '<':
                devcsql= devcsql + ' AND `d`.' + attr['attrib'] + ' < %s'
                filter_params.append(attr['value'])
            elif attr['condition'] == 'equals' or attr['condition'] == 'eq' or attr['condition'] == 'is' or attr['condition'] == '==' or  attr['condition'] == '=':
                devcsql= devcsql + ' AND `d`.' + attr['attrib'] + ' = %s'
                filter_params.append(attr['value'])
            elif attr['condition'] == 'in':
                value = attr['value'].split(',')
                devcsql = devcsql + ' AND `d`.' + attr['attrib'] + " IN ('%s')" % ("','".join(str(x) for x in value))
        #print devcsql
        #print filter_params
        count = db.one(sql=devcsql, param=filter_params)
        if count > 0:
            ret = True
        else:
            ret = False
        return ret

    @classmethod
    def cache_device_conditions(cls,db,dev_id):
        result = {}
        with dbutil.Session() as db:
            devsql = "SELECT device_id FROM devices"
            sql = "SELECT * FROM `alert_tests`"
            assocsql = "SELECT * FROM `alert_assoc`"
            devices = db.all(sql=devsql)
            alerts = db.all(sql=sql)
            assocs = db.all(sql=assocsql)
            cache_condition = defaultdict( lambda: defaultdict(lambda: defaultdict(lambda: defaultdict( dict ))))
            cond_new = defaultdict(lambda: defaultdict( dict ))
            for alert in alerts:
                cache_condition['cond'][str(alert['alert_test_id'])] = alert
                cache_condition['cond'][str(alert['alert_test_id'])]['entity_type'] = alert['entity_type']
                cache_condition['cond'][str(alert['alert_test_id'])]['conditions'] = alert['conditions']
                cache_condition['cond'][str(alert['alert_test_id'])]['assoc'] = {}
            for assoc in assocs:
                cache_condition['assoc'][str(assoc['alert_assoc_id'])] = assoc
                cache_condition['assoc'][str(assoc['alert_assoc_id'])]['entity_attribs'] = simplejson.loads(assoc['entity_attribs'])
                cache_condition['assoc'][str(assoc['alert_assoc_id'])]['device_attribs'] = simplejson.loads(assoc['device_attribs'])

            for assoc_id in cache_condition['assoc'].keys():
                if AlertWriter.match_device(db, dev_id, cache_condition['assoc'][assoc_id]['device_attribs']):
                    cache_condition['cond'][str(cache_condition['assoc'][assoc_id]['alert_test_id'])]['assoc'][assoc_id] = cache_condition['assoc'][assoc_id]
                    cond_new['cond'][str(cache_condition['assoc'][assoc_id]['alert_test_id'])] = cache_condition['cond'][str(cache_condition['assoc'][assoc_id]['alert_test_id'])]
                else:
                    del cache_condition['assoc'][assoc_id]
            result = cond_new
        return result

    @classmethod
    def update_device_alert_table(cls):
        result = {}
        ret = False
        with dbutil.Session() as db:
            devsql = "SELECT device_id FROM devices"
            devices = db.all(sql=devsql)
            #alert_table = defaultdict( lambda: defaultdict(lambda: defaultdict(lambda: defaultdict( dict ))))
            #conditions = AlertWriter.cache_device_conditions(db)
            for dev in devices:
                conditions = AlertWriter.cache_device_conditions(db, dev['device_id'])

                alert_table = defaultdict( lambda: defaultdict(lambda: defaultdict(lambda: defaultdict( dict ))))
                for alert_test_id in conditions['cond']:
                    #print simplejson.dumps(conditions['cond'][alert_test_id])
                    assocs_tmp = []
                    for assoc_id in conditions['cond'][alert_test_id]['assoc']:
                        entities = AlertWriter.match_device_entities(db, dev['device_id'], conditions['cond'][alert_test_id]['assoc'][assoc_id]['entity_attribs'], conditions['cond'][alert_test_id]['assoc'][assoc_id]['entity_type'])
                        for entity in entities:
                            if int(assoc_id) not in assocs_tmp:
                                assocs_tmp.append(int(assoc_id))
                    for assoc_id in conditions['cond'][alert_test_id]['assoc']:
                        for entity in entities:
                             alert_table[conditions['cond'][alert_test_id]['assoc'][assoc_id]['entity_type']]['%s' % entity['%s_id' % conditions['cond'][alert_test_id]['assoc'][assoc_id]['entity_type']]][alert_test_id] = assocs_tmp
                result[dev['device_id']] = alert_table
            cur_alert_table = AlertWriter.getcurrent_alert_table(db)

            for dev in result:
                for entity_type in result[dev]:
                    for entity_id in result[dev][entity_type]:
                        for alert_id in result[dev][entity_type][entity_id]:
                            #print cur_alert_table[entity_type][str(entity_id)][str(alert_id)]
                            #print 'abc: %s' % cur_alert_table[entity_type][entity_id][alert_id]
                            if cur_alert_table[dev][entity_type][entity_id][alert_id]:
                                #print 'dev %s alert_assocs %s' % (dev,cur_alert_table[dev][entity_type][entity_id][alert_id]['alert_assocs'])
                                if ',' in cur_alert_table[dev][entity_type][entity_id][alert_id]['alert_assocs']:
                                    comparedString = cur_alert_table[dev][entity_type][entity_id][alert_id]['alert_assocs'].split(',')
                                    comparedString = [ int(tmp) for tmp in comparedString]
                                    #print 'result %s' % result[dev][entity_type][entity_id][alert_id]
                                    if not set(comparedString)- set(result[dev][entity_type][entity_id][alert_id]):
                                        #means data is the same
                                        del cur_alert_table[dev][entity_type][entity_id][alert_id]
                                    else:
                                        #have to update db
                                        build_assoc_id = ''
                                        for new_assoc_id in result[dev][entity_type][entity_id][alert_id]:
                                            if len(result[dev][entity_type][entity_id][alert_id]) > 1:
                                                build_assoc_id = new_assoc_id + ","
                                            else:
                                                build_assoc_id = new_assoc_id
                                        #print build_assoc_id
                                        command = "UPDATE alert_table SET alert_assocs=%s WHERE `alert_table_id`= %s"
                                        ret = db.execute(sql=command, param=(build_assoc_id, cur_alert_table[dev][entity_type][entity_id][alert_id]['alert_table_id']))
                                else:
                                    if int(cur_alert_table[dev][entity_type][entity_id][alert_id]['alert_assocs']) == result[dev][entity_type][entity_id][alert_id][0]:
                                        del cur_alert_table[dev][entity_type][entity_id][alert_id]
                                    else:
                                        # single data,have to update db
                                        command = "UPDATE alert_table SET alert_assocs=%s WHERE `alert_table_id`= %s"
                                        ret = db.execute(sql=command, param=(build_assoc_id, cur_alert_table[dev][entity_type][entity_id][alert_id]['alert_table_id']))

                            else:
                                #insertDB
                                alert_table = {}
                                alert_table['device_id'] = dev
                                alert_table['entity_type'] = entity_type
                                alert_table['entity_id'] = entity_id
                                alert_table['alert_test_id'] = alert_id
                                alert_table['alert_assocs'] = result[dev][entity_type][entity_id][alert_id][0]
                                ret = db.insert('alert_table', alert_table)
            #print 'check cur_table %s' % simplejson.dumps(cur_alert_table)
            for dev in cur_alert_table:
                for entity_type in cur_alert_table[dev]:
                    #print cur_alert_table[dev][entity_type]
                    for entity_id in cur_alert_table[dev][entity_type]:
                        for alert_id in cur_alert_table[dev][entity_type][entity_id]:
                            if 'alert_table_id' in cur_alert_table[dev][entity_type][entity_id][alert_id]:
                                print 'delete unhandled alert_table'
                                #db.execute('DELETE FROM alert_setting_devices WHERE alert_setting_id=%(alert_setting_id)s', param=alert_setting)
                                cmd = "DELETE FROM alert_table WHERE `alert_table_id`=%s"
                                ret = db.execute(sql=cmd, param=cur_alert_table[dev][entity_type][entity_id][alert_id]['alert_table_id'])
        return ret

    @classmethod
    def add_alert_setting(cls, alert_setting=None):
        result = {}
        with dbutil.Session() as db:
            # Insert alert
            #{"value":"60","condition":"gt","metric":"processor_usage"}
            build_alert_setting = {}
            build_alert_assoc = {}
            build_alert_setting['conditions'] = {'metric': alert_setting['condition_metric'], 'condition': alert_setting['condition_symbol'], 'value': alert_setting['condition_value'], 'attrib':'*'}
            build_alert_setting['conditions'] = simplejson.dumps([build_alert_setting['conditions']])
            build_alert_setting['`entity_type`'] = alert_setting['entity_type']

            build_alert_setting['`alert_name`'] = alert_setting['alert_name']
            build_alert_setting['`alert_message`'] = alert_setting['alert_message']
            build_alert_setting['severity'] = 'crit'
            build_alert_setting['suppress_recovery'] = 0
            build_alert_setting['`and`'] = '1'
            build_alert_setting['delay'] = '0'
            build_alert_setting['enable'] = '1'

            devcsql = "SELECT COUNT(device_id) FROM devices"
            devTotal = db.one(sql=devcsql)
            if len(alert_setting['devices']) == devTotal:
                build_alert_assoc['device_attribs'] = simplejson.dumps([{'value':None, 'condition':None, 'attrib':'*', 'metric':alert_setting['condition_metric']}])
            else:
                hostname_list = []
                for dev_id in alert_setting['devices']:
                    hostname = DeviceReader.get_device_host_by_id(dev_id['device_id'])
                    hostname_list.append("{}".format(hostname['hostname']))
                build_hostname_list = "{}".format(','.join(hostname_list))
                build_alert_assoc['device_attribs'] = simplejson.dumps([{'value':build_hostname_list, 'condition':'in', 'attrib':'hostname', 'metric':alert_setting['condition_metric']}])

            db.insert('alert_tests', build_alert_setting)
            alert_setting_id = db.cur.lastrowid

            build_alert_assoc['alert_test_id'] = alert_setting_id
            build_alert_assoc['entity_type'] = alert_setting['entity_type'];
            build_alert_assoc['enable'] = '1'
            build_alert_assoc['entity_attribs'] = simplejson.dumps([{'value': alert_setting['entity_attribute']['value'], 'condition': alert_setting['entity_attribute']['condition'], 'attrib': alert_setting['entity_attribute']['attrib'], 'metric': alert_setting['condition_metric']}])
            db.insert('alert_assoc', build_alert_assoc)
        return result
    @classmethod
    def update_alert_setting(cls, alert_setting=None, force=False):
        result = {}
        ret = False
        with dbutil.Session() as db:
            build_alert_assoc = {}
            devcsql = "SELECT COUNT(device_id) FROM devices"
            devTotal = db.one(sql=devcsql)
            if len(alert_setting['devices']) == devTotal:
                build_alert_assoc['device_attribs'] = simplejson.dumps([{'value':None, 'condition':None, 'attrib':'*', 'metric':alert_setting['condition_metric']}])
            else:
                hostname_list = []
                for dev_id in alert_setting['devices']:
                    hostname = DeviceReader.get_device_host_by_id(dev_id['device_id'])
                    hostname_list.append("{}".format(hostname['hostname']))
                build_hostname_list = "{}".format(','.join(hostname_list))
                build_alert_assoc['device_attribs'] = simplejson.dumps([{'value':build_hostname_list, 'condition':'in', 'attrib':'hostname', 'metric':alert_setting['condition_metric']}])

            build_alert_assoc['entity_attribute'] = simplejson.dumps([{'value':alert_setting['alert_assoc'][0]['entity_attribute'][0]['value'], 'condition': alert_setting['alert_assoc'][0]['entity_attribute'][0]['condition'], 'attrib': alert_setting['alert_assoc'][0]['entity_attribute'][0]['attrib']}])
            command = "UPDATE `alert_assoc` SET device_attribs=%s,entity_attribs=%s WHERE `alert_assoc_id`= %s"
            ret = db.execute(sql=command, param=( build_alert_assoc['device_attribs'],build_alert_assoc['entity_attribute'], alert_setting['alert_assoc'][0]['alert_assoc_id']))
            #condition , name , message are chaned
            build_alert_setting = {}
            build_alert_setting['conditions'] = simplejson.dumps([{'metric': alert_setting['condition_metric'], 'condition': alert_setting['condition_symbol'], 'value': alert_setting['condition_value'], 'attrib':'*'}])

            command =  "UPDATE `alert_tests` SET `alert_name`=%s, `alert_message`=%s, `conditions`=%s WHERE `alert_test_id`= %s"
            ret = db.execute(sql=command, param=(alert_setting['alert_name'], alert_setting['alert_message'], build_alert_setting['conditions'], alert_setting['alert_setting_id']))
            ret = AlertWriter.update_device_alert_table()
        return ret
    @classmethod
    def delete_alert_settings(cls, alert_settings):
        ret = False
        with dbutil.Session() as db:
            for alert_setting in alert_settings:
                if alert_setting.get('alert_setting_id', None):
                    ret = db.execute('DELETE FROM alert_tests WHERE alert_test_id=%s',param= alert_setting['alert_setting_id'])
                    ret = db.execute('DELETE FROM alert_table WHERE alert_test_id=%s',param= alert_setting['alert_setting_id'])
                    ret = db.execute('DELETE FROM alert_assoc WHERE alert_test_id=%s',param= alert_setting['alert_setting_id'])
        return ret

class AlertLogReader(object):
    @classmethod
    def get_snmp_alertlog(cls, device_id=None, entity_type=None, sensor_id=None, alert_status=None,
        start_time="", end_time="", cur_page=1, page_size=50, order_by=None, sort=None):

        #ToDo: query by sensor_id, and sensor_type. (Maybe same sesnor_id but different sensor_type)
        translate_to_table = {'processor':'processors', 'mempool':'mempools', 'sensor':'sensors', 'status':'status', "storage":"storage", "port":"ports", 'device': 'devices'}
        filter_cmd = ""
        filter_params = []
        result = {}
        datas = []
        cache_entity_type_and_id_list = []
        cache_alert_table = []
        #print 'device_id %s' % device_id
        with dbutil.Session() as db:
            alert_logs = []
            typesql = "SELECT DISTINCT entity_type,entity_id from alert_log"
            e_types = db.all(sql=typesql)
            alertstatussql = "SELECT alert_test_id,entity_id, entity_type,alert_status from alert_table"
            cache_alert_table = db.all(sql=alertstatussql)
            if start_time:
                filter_cmd = " AND timestamp between FROM_UNIXTIME(%s) and FROM_UNIXTIME(%s) "
                filter_params.append(start_time)
                filter_params.append(end_time)
            else:
                filter_cmd = "AND timestamp is not NULL "
            if device_id:
                filter_cmd = filter_cmd + " and alert_log.device_id = %s "
                filter_params.append(device_id)
            if entity_type:
                filter_cmd = filter_cmd + " and alert_log.entity_type = %s "
                filter_params.append(entity_type)
            order_cmd = " ORDER BY "
            order_cmd = order_cmd + "on_time DESC"
            csql = "SELECT count(alert_log.entity_id), timestamp as on_time FROM `alert_log` WHERE `log_type` IN (2,5) AND alert_test_id IN (SELECT alert_test_id from alert_tests)" + filter_cmd
            sql = "SELECT alert_log.event_id, alert_log.entity_id, alert_log.entity_type,alert_log.log_type as status, alert_log.alert_test_id as alert_setting_id, alert_log.device_id, DATE_FORMAT(`alert_log`.`timestamp`, '%%Y-%%m-%%d %%H:%%i:%%S')as on_time, UNIX_TIMESTAMP(`alert_log`.`timestamp`) as `unixtime`,alert_log.message ,B.conditions, B.alert_name, C.hostname FROM `alert_log` LEFT JOIN `alert_tests` AS B ON alert_log.alert_test_id = B.alert_test_id LEFT JOIN `devices` as C on alert_log.device_id = C.device_id WHERE `log_type` IN (2,5) AND B.alert_test_id IN (SELECT alert_test_id from alert_tests)" + filter_cmd + order_cmd + " LIMIT %s, %s"
            total = db.one(sql=csql, param=filter_params)

            filter_params.append((cur_page-1)*page_size)
            filter_params.append(page_size)
            ret = db.all(sql = sql , param=filter_params )
            alert_logs.extend(ret)

            for e_type in e_types:
                if e_type['entity_type'] == 'port':
                    descr = 'ifDescr'
                elif e_type['entity_type'] == 'device':
                    descr = None
                else:
                    descr= '%s_descr' % e_type['entity_type']
                sensor_id = str('%s_id' % e_type['entity_type'])
                if descr:
                    detailsql = "SELECT `%s` as name, `%s` as sensor_id FROM `%s` WHERE `%s` = %s" % (descr , sensor_id ,translate_to_table[e_type['entity_type']], sensor_id, e_type['entity_id'])
                else:
                    detailsql = "SELECT `%s` as name , device_id as sensor_id FROM `%s` WHERE `device_id` = %s" % ("hostname" ,translate_to_table[e_type['entity_type']],  e_type['entity_id'])
                ret = db.row(sql = detailsql)
                if ret:
                    ret['entity_type'] = e_type['entity_type']
                    cache_entity_type_and_id_list.append(ret)
                    #LOG.info(simplejson.dumps(cache_entity_type_and_id_list))
            for alert_log in alert_logs:
                for cache_list in cache_entity_type_and_id_list:
                    if alert_log['entity_id'] == cache_list['sensor_id'] and alert_log['entity_type'] == cache_list['entity_type']:
                        alert_log['name'] = cache_list['name']

            result['total'] = total
            result['datas'] = alert_logs

        return result


    @classmethod
    def get_snmp_alertlog_match_qrmplus(cls, device_id=None, sensor_id=None, alert_status=None,
        start_time="", end_time="", cur_page=1, page_size=20, order_by=None, sort=None):
        filter_cmd = ""
        filter_params = []
        result = {}
        datas = []
        processor_list = []
        port_list = []
        #step 1, get DISTINCT entity_type,entity_id
        typesql = "SELECT DISTINCT entity_type,entity_id from alert_log"
        if device_id:
            filter_cmd = filter_cmd + " and alert_log.device_id = %s "
            filter_params.append(device_id)
        order_cmd = " ORDER BY "
        if order_by:
            if sort:
                order_cmd = order_cmd + order_by + " " + sort + ", "
            else:
                order_cmd = order_cmd + order_by + " , "

        order_cmd = order_cmd + "on_time DESC"

        sql = "SELECT alert_log.entity_id, alert_log.entity_type, alert_log.alert_test_id, alert_log.device_id, alert_log.timestamp as on_time, B.conditions, C.hostname FROM `alert_log` LEFT JOIN `alert_tests` AS B ON alert_log.alert_test_id = B.alert_test_id LEFT JOIN `devices` as C on alert_log.device_id = C.device_id WHERE `log_type` = 2 AND B.alert_test_id IN (SELECT alert_test_id from alert_tests) " + filter_cmd
        with dbutil.Session() as db:
            e_types = db.all(sql=typesql)
            alert_logs = [] 
            for e_type in e_types:
                ret = db.all(sql = sql + " " + "AND alert_log.entity_type="+"'" +e_type['entity_type']+ "'" + " " + "AND alert_log.entity_id=" + str(e_type['entity_id']) + order_cmd, param=filter_params )
                if ret:
                    alert_logs.extend(ret)
                for i in range(len(alert_logs)):
                    data = {}
                    if len(alert_logs) > (i + 1):
                        ret = db.row(sql= "SELECT * FROM `alert_log` WHERE `entity_id` = "  + str(e_type['entity_id']) + " AND `log_type` = 5 AND `entity_type`=" + "'" + e_type['entity_type'] + "'" + " AND `timestamp` BETWEEN %s and %s", param=(alert_logs[i]['on_time'], alert_logs[i+1]['on_time']))
                        if ret:
                            alert_logs[i]['off_time'] = ret['timestamp']
                            alert_logs[i]['alert_status'] = '0' 
                    else:
                        alert_logs[i]['off_time'] = "N/A"
                        alert_logs[i]['alert_status'] = '1'
            result['datas'] = alert_logs
            
        return result


class EventLogReader(object):
    @classmethod
    def get_eventlog(cls, start_time=None, end_time=None):
        result = {}
        with dbutil.Session() as db:
            print start_time
            print end_time
            #timezone = db.row(sql="SELECT EXTRACT(HOUR FROM (TIMEDIFF(NOW(), UTC_TIMESTAMP))) AS `timezone`")
            #if timezone['timezone'] > 0:
            #    timezone = "+%s:00" % timezone['timezone']
            #else:
            #    timezone = "%s:00" % timezone['timezone']
            if start_time and end_time:
                #sql = "SELECT `eventlog`.*, CONVERT_TZ(`eventlog`.`timestamp`, %s, %s) as `unixtime`, \
                #      `devices`.`hostname` FROM `eventlog` LEFT JOIN `devices` ON `eventlog`.device_id = `devices`.device_id \
                #      WHERE timestamp BETWEEN %s AND %s"

                sql = "SELECT `eventlog`.`device_id`, `eventlog`.`event_id`, `eventlog`.`message`, `eventlog`.`entity_type`,\
                      `eventlog`.`entity_id`, `eventlog`.`severity`,\
                      UNIX_TIMESTAMP(`eventlog`.`timestamp`) as `unixtime`,\
                      DATE_FORMAT(`eventlog`.`timestamp`, '%%Y-%%m-%%d %%H:%%i:%%S') as date_time , \
                      `devices`.`hostname` FROM `eventlog` LEFT JOIN `devices` ON `eventlog`.`device_id` = `devices`.`device_id` \
                      WHERE `eventlog`.`timestamp` BETWEEN FROM_UNIXTIME(%s) AND FROM_UNIXTIME(%s)"
                result = db.all(sql=sql, param=(start_time, end_time))
            else:
                #sql = "SELECT `eventlog`.`device_id`,`eventlog`.`event_id`, `eventlog`.`message`, `eventlog`.`entity_type`, \
                #      `eventlog`.`entity_id`, `eventlog`.`severity`, \
                #      DATE_FORMAT(`eventlog`.`timestamp`, '%%Y-%%m-%%d %%H:%%i:%%S') as timestamp ,\
                #       UNIX_TIMESTAMP(CONVERT_TZ(`eventlog`.`timestamp`, %s, %s) as `unixtime`, \
                #      `devices`.`hostname` FROM `eventlog` LEFT JOIN `devices` ON `eventlog`.device_id = `devices`.device_id \
                #      ORDER BY `event_id` DESC LIMIT 0,15"
                #sql = "SELECT `eventlog`.*, CONVERT_TZ(`eventlog`.`timestamp`, %s, %s) as `unixtime`,\
                #      `devices`.`hostname` FROM `eventlog` LEFT JOIN `devices` ON `eventlog`.device_id = `devices`.device_id \
                #      ORDER BY `event_id` DESC LIMIT 0,15"
                sql = "SELECT `eventlog`.`device_id`, `eventlog`.`event_id`, `eventlog`.`message`, `eventlog`.`entity_type`,\
                      `eventlog`.`entity_id`, `eventlog`.`severity`,\
                      UNIX_TIMESTAMP(`eventlog`.`timestamp`) as `unixtime`,\
                      DATE_FORMAT(`eventlog`.`timestamp`, '%Y-%m-%d %H:%i:%S') as date_time ,\
                      `devices`.`hostname` FROM `eventlog` LEFT JOIN `devices` ON `eventlog`.`device_id` = `devices`.`device_id` \
                      ORDER BY `event_id` DESC LIMIT 0,15"
                result = db.all(sql=sql)

        return result

class LiveDataReader(object):
    @classmethod
    def get_livedata(cls, device_id, metric, metric_id):
        result = {}
        tables = {'processors':'processor', 'mempools':'mempool', 'status':'status', 'sensors':'sensor', "storage":"storage"}
        with dbutil.Session() as db:
            #result = db.all(sql="SELECT *, `storage`.`storage_id` AS `storage_id` FROM `storage` WHERE 1 AND (( (`device_id` != '' AND `device_id` IS NOT NULL))) AND `storage`.`device_id` = %s AND `storage`.`storage_ignore` = '0' AND `storage`.`storage_id` = %s", param=(device_id, storage_id))
            constructmetric = {}
            if metric  == "processors":
                value = db.row(sql="SELECT *, " + metric + "." + tables[metric] + "_id AS " + tables[metric] + "_id FROM " + metric + \
                    " WHERE 1 AND (( (`device_id` != '' AND `device_id` IS NOT NULL))) AND " + metric + ".`device_id` = %s AND " + \
                    metric + "." + tables[metric] + "_id = %s", param=(device_id, metric_id))
                if value is None:
                    LOG.warning('id not found')
                    raise KeyError('id not found')
                constructmetric["metric"] = metric
                constructmetric["value"] = value["%s_usage" % tables[metric]]
                constructmetric["metric_id"] = metric_id
                result['time'] = int(time.time())
                result['metrics'] = constructmetric
            elif metric == "mempools":
                constructvalue = {}
                value = db.row(sql="SELECT *, " + metric + "." + tables[metric] + "_id AS " + tables[metric] + "_id FROM " + metric + \
                    " WHERE 1 AND (( (`device_id` != '' AND `device_id` IS NOT NULL))) AND " + metric + ".`device_id` = %s AND " + \
                    metric + "." + tables[metric] + "_deleted = '0' AND " + metric + "." + tables[metric] + "_id = %s", param=(device_id, metric_id))
                if value is None:
                    LOG.warning('id not found')
                    raise KeyError('id not found')
                constructmetric["metric"] = metric
                constructmetric["metric_id"] = metric_id
                constructvalue["mempool_used"] = value["mempool_used"]
                constructvalue["mempool_total"] = value["mempool_total"]
                constructvalue["mempool_free"] = value["mempool_free"]
                constructvalue["mempool_perc"] = value["mempool_perc"]
                constructmetric["value"] = constructvalue
                result['time'] = int(time.time())
                result['metrics'] = constructmetric
            elif metric == "sensors":
                value = db.row(sql="SELECT *, " + metric + "." + tables[metric] + "_id AS " + tables[metric] + "_id FROM " + metric + \
                    " WHERE 1 AND (( (`device_id` != '' AND `device_id` IS NOT NULL))) AND " + metric + ".`device_id` = %s AND " + \
                    metric + "." + tables[metric] + "_deleted = '0' AND " + metric + "." + tables[metric] + "_id = %s", param=(device_id, metric_id))
                if value is None:
                    LOG.warning('id not found')
                    raise KeyError('id not found')
                constructvalue = {}
                constructmetric["metric"] = metric
                constructmetric["metric_id"] = metric_id
                constructvalue["sensor_limit_low_warn"] = value ["sensor_limit_low_warn"]
                constructvalue["sensor_custom_limit"] = value["sensor_custom_limit"]
                constructvalue["sensor_limit_low"] = value["sensor_limit_low"]
                constructvalue["sensor_limit"] = value["sensor_limit"]
                constructvalue["sensor_limit_warn"] = value["sensor_limit_warn"]
                constructvalue["sensor_value"] = value["sensor_value"]
                constructmetric["value"] = constructvalue
                result['time'] = int(time.time())
                result['metrics'] = constructmetric
            elif metric == "status":
                value = db.row(sql="SELECT *, " + metric + "." + tables[metric] + "_id AS " + tables[metric] + "_id FROM " + metric + \
                    " WHERE 1 AND (( (`device_id` != '' AND `device_id` IS NOT NULL))) AND " + metric + ".`device_id` = %s AND " + \
                    metric + "." + tables[metric] + "_deleted = '0' AND " + metric + "." + tables[metric] + "_id = %s", param=(device_id, metric_id))
                if value is None:
                    LOG.warning('id not found')
                    raise KeyError('id not found')
                constructmetric["metric"] = metric
                constructmetric["metric_id"] = metric_id
                constructmetric["value"] = value["%s_name" % tables[metric]]
                result['time'] = int(time.time())
                result['metrics'] = constructmetric
            elif metric == "storage":
                value = db.row(sql="SELECT *, " + metric + "." + tables[metric] + "_id AS " + tables[metric] + "_id FROM " + metric + \
                    " WHERE 1 AND (( (`device_id` != '' AND `device_id` IS NOT NULL))) AND " + metric + ".`device_id` = %s AND " + \
                    metric + "." + tables[metric] + "_deleted = '0' AND " + metric + "." + tables[metric] + "_id = %s", param=(device_id, metric_id))
                constructvalue = {}
                if value is None:
                    LOG.warning('id not found')
                    raise KeyError('id not found')
                constructmetric["metric"] = metric
                constructmetric["metric_id"] = metric_id
                constructvalue["storage_used"] = value["storage_used"]
                constructvalue["storage_size"] = value["storage_size"]
                constructmetric["value"] = constructvalue
                result['time'] = int(time.time())
                result['metrics'] = constructmetric
            #result = db.all(sql="SELECT *, " + metric + "." + tables[metric] + "_id AS " + tables[metric] + "_id FROM " + metric + \
            #        " WHERE 1 AND (( (`device_id` != '' AND `device_id` IS NOT NULL))) AND " + metric + ".`device_id` = %s AND " + \
            #        metric + "." + tables[metric] + "_ignore = '0' AND " + metric + "." + tables[metric] + "_id = %s", param=(device_id, metric_id))

        return result

    @classmethod
    def get_livedata_by_sensor_table(cls, device_id, sensor_table):
        result = {}
        tables = {'processors':'processor', 'mempools':'mempool', 'status':'status', 'sensors':'sensor', "storage":"storage"}
        with dbutil.Session() as db:
            #result = db.all(sql="SELECT *, `storage`.`storage_id` AS `storage_id` FROM `storage` WHERE 1 AND (( (`device_id` != '' AND `device_id` IS NOT NULL))) AND `storage`.`device_id` = %s AND `storage`.`storage_ignore` = '0' AND `storage`.`storage_id` = %s", param=(device_id, storage_id))
            constructmetric = {}
            if sensor_table  == "processors":
                sqlstring = "SELECT  " + sensor_table + "." + tables[sensor_table] + "_usage AS " +  "value " + "," + \
                             sensor_table + "." + tables[sensor_table] + "_id AS " + "metric_id " + "," + \
                             sensor_table + "." + tables[sensor_table] + "_descr AS " +  "name " + " FROM " + sensor_table + \
                    " WHERE 1 AND (( (`device_id` != '' AND `device_id` IS NOT NULL))) AND " + sensor_table + ".`device_id` = %s"
                values = db.all(sql = sqlstring, param=device_id )
                if values is None:
                    LOG.warning('id not found')
                    raise KeyError('id not found')
                result['time'] = int(time.time())
                result['metrics'] = values
            elif sensor_table == "mempools":
                sqlstring = "SELECT  " + sensor_table + "." + tables[sensor_table] + "_used " + "," + \
                             sensor_table + "." + tables[sensor_table] + "_total " + "," + \
                             sensor_table + "." + tables[sensor_table] + "_free " + "," + \
                             sensor_table + "." + tables[sensor_table] + "_perc " + "," + \
                             sensor_table + "." + tables[sensor_table] + "_id AS " + "metric_id " + "," + \
                             sensor_table + "." + tables[sensor_table] + "_descr AS " + "name " + " FROM " + sensor_table + \
                    " WHERE 1 AND (( (`device_id` != '' AND `device_id` IS NOT NULL))) AND " + sensor_table + ".`device_id` = %s"
                values = db.all(sql = sqlstring, param=device_id )
                if values is None:
                    LOG.warning('id not found')
                    raise KeyError('id not found')
                result['time'] = int(time.time())
                result['metrics'] = values
            elif sensor_table == "storage":
                sqlstring = "SELECT  " + sensor_table + "." + tables[sensor_table] + "_used " + "," + \
                             sensor_table + "." + tables[sensor_table] + "_size " + "," + \
                             sensor_table + "." + tables[sensor_table] + "_id AS " + "metric_id " + "," + \
                             sensor_table + "." + tables[sensor_table] + "_descr AS " + "name " + " FROM " + sensor_table + \
                    " WHERE 1 AND (( (`device_id` != '' AND `device_id` IS NOT NULL))) AND " + sensor_table + ".`device_id` = %s"
                values = db.all(sql = sqlstring, param=device_id ) 
                if values is None:
                    LOG.warning('id not found')
                    raise KeyError('id not found')
                result['time'] = int(time.time())
                result['metrics'] = values
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
            if not os.path.exists(rrdfile):
                LOG.warning('rrdfile not found')
                raise KeyError('rrdfile not found')
            if start_time is None and end_time is None:
                ret = rrdtool.fetch(str(rrdfile), "AVERAGE")
            else:
                ret = rrdtool.fetch(str(rrdfile), 'AVERAGE', '-s %s' % start_time, '-e %s' % end_time)
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
                       #data['%s' % timestamp] = ["%.2f" % if detailvalue else "" for detailvalue in value]
                       data['%s' % timestamp] = [round(detailvalue,2) if detailvalue else 0.0 for detailvalue in value]
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

#class LiveDataReader(object):

#    @classmethod
#    def get_snmp_live_data(cls, device_id, table, metric_id, start_time=None, end_time=None):
        







#print DeviceReader().get_device_detail_by_id(15)
