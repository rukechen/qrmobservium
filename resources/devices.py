from flask_restful import request, reqparse, abort, fields, marshal
from qrmobservium.resources.base_resource import BaseResource
from qrmobservium.common import status_codes, logger
from qrmobservium.common.errors import DeviceNotExistError, AccessDatabaseError, DeviceAlreadyExistError, InvalidParametersError
from qrmobservium.common.utility import is_valid_ip_address
import rrdtool
import subprocess, sys, shlex

LOG = logger.Logger(__name__)

device_mgt_parser = reqparse.RequestParser()
device_mgt_parser.add_argument('jid', type=str, location='json', required=True)
device_mgt_parser.add_argument('devices', type=list, location='json', default=[], help='devices')


device_detailinfo_parser = reqparse.RequestParser()
device_detailinfo_parser.add_argument('jid', type=str, location='json', required=True)
device_detailinfo_parser.add_argument('device_id', type=str, location='json', required=True)

device_arp_parser = reqparse.RequestParser()
device_arp_parser.add_argument('page', type=int, location='args', default=1)
device_arp_parser.add_argument('limit', type=int, location='args', default=50)

device_fdb_parser = reqparse.RequestParser()
device_fdb_parser.add_argument('page', type=int, location='args', default=1)
device_fdb_parser.add_argument('limit', type=int, location='args', default=50)

def execute_cmd(cmd):
    try:
        #print cmd
        message = subprocess.Popen(cmd,
                          shell=True,
                          stdout = subprocess.PIPE,
                          stderr=subprocess.PIPE).communicate()
        #print "execute_result: " + str(message)
        if message[0] == "":
            #if message[0] is empty, we would like to konw message[1]
            return message[1]

        return message[0]
    except:
        e = sys.exc_info()[0]
        print "[Error] execute_cmd: " + str(e)
        return False

class DeviceDataCollecting(BaseResource):
    def get(self):
        mesg = {}
        try:
            ret = rrdtool.fetch("/opt/observium/rrd/172.17.30.14/processor-hr-768.rrd","AVERAGE")
            #print ret
            mesg['starttime'] = ret[0][0]
            mesg['endtime']   = ret[0][1]
            mesg['datas'] = ret[2]
        except Exception as e:
            print e
        return mesg


class DeviceUpdate(BaseResource):
    def post(self):
        try:
            ret = execute_cmd("/usr/bin/env php /opt/observium/poller.php -h 172.17.30.15")
            #print ret
        except Exception as e:
            print e
        return "", status_codes.HTTP_200_OK

class DeviceManage(BaseResource):
    def delete(self):
        args = device_mgt_parser.parse_args()

        task_msg = {
            'jid':args['jid'],
            'devices':args['devices'],
            'task_dev_count':len(args['devices']),
            'task_status':'start',
            'task_detail':'remove_devices',
            'desc':'remove_devices',
            'task_name':'device_discovery'
        }
        try:
            for dev in task_msg['devices']:
                #print 'dev %s' % dev
                if not dev['device_id']:
                    raise DeviceNotExistError
                result = self.app.get_device_reader().get_device_host_by_id(dev['device_id'])
                ret = execute_cmd("/usr/bin/env php /opt/observium/delete_device.php %s rrd" % result['hostname'])
                #print 'command result %s' % ret
        except DeviceNotExistError as e:
            raise e
        except Exception as e:
            abort(status_codes.HTTP_404_NOT_FOUND, message="Device not found")

        return "", status_codes.HTTP_201_CREATED


    def post(self):
        mesg = {}
        args = device_mgt_parser.parse_args()
        devices = args['devices']
        task_msg = {
            'jid':args['jid'],
            'devices':devices,
            'task_dev_count':len(devices),
            'task_detail':'add_devices',
            'desc':'add_devices',
        }
        try:
            for dev in task_msg['devices']:
                if not is_valid_ip_address(dev['ip']):
                    raise InvalidParametersError
                #print 'dev %s %s '% (dev['ip'], dev['community'])
                if dev['snmpversion'] == 'v3':
                    if not dev['level']:
                        raise InvalidParametersError
                    if dev['level'] == 'authNoPriv':
                        if not dev['username'] or not dev['password'] or not dev['auth_protocol']:
                            raise InvalidParametersError
                        if len(shlex.split(dev['username'])) >= 2 or len(shlex.split(dev['password'])) >= 2 \
                           or len(shlex.split(dev['auth_protocol'])) >= 2:
                            raise InvalidParametersError
                        ret = execute_cmd("/usr/bin/env php /opt/observium/add_device.php %s %s %s %s %s %s" % \
                            (dev['ip'], 'authNoPriv', 'v3', dev['username'], \
                             dev['password'], dev['auth_protocol']))
                    elif dev['level'] == 'authPriv':
                        if not dev['username'] or not dev['password'] or not dev['auth_protocol'] \
                            or not dev['priv_protocol'] or not dev['enckey']:
                            raise InvalidParametersError
                        if len(shlex.split(dev['username'])) >= 2 or len(shlex.split(dev['password'])) >= 2 \
                           or len(shlex.split(dev['auth_protocol'])) >= 2 or len(shlex.split(dev['enckey'])) >= 2 \
                           or len(shlex.split(dev['priv_protocol'])) >= 2:
                            raise InvalidParametersError
                        ret = execute_cmd("/usr/bin/env php /opt/observium/add_device.php %s %s %s %s %s %s %s %s" % \
                            (dev['ip'], 'authPriv', 'v3', dev['username'], dev['password'], \
                             dev['enckey'], dev['auth_protocol'], dev['priv_protocol']))
                        #print ret
                    else:
                        ret = execute_cmd("/usr/bin/env php /opt/observium/add_device.php %s %s" % (dev['ip'], "noAuthNoPriv" ))
                else:
                    if not dev['community']:
                        raise InvalidParametersError
                    if len (shlex.split(dev['community'])) >= 2:
                        raise InvalidParametersError
                    ret = execute_cmd("/usr/bin/env php /opt/observium/add_device.php  %s %s" % (dev['ip'], dev['community']))
                #print ret
                #Devices failed
                #Added device 172.17.30.98 (25)
                if 'success' in ret:
                    #get_device_detail_by_hostname
                    mesg = self.app.get_device_reader().get_device_id_by_host(dev['ip'])
                    #print 'added successfully'
                elif 'Already got device' in ret:
                    raise DeviceAlreadyExistError
                else:
                    raise DeviceNotExistError
        except DeviceNotExistError as e:
            raise e
        except InvalidParametersError as e:
            raise e
        except DeviceAlreadyExistError as e:
            raise e
        except Exception as e:
            abort(status_codes.HTTP_404_NOT_FOUND, message="Device not found")
        #issue_device_mgt_command(self.app, task_msg)

        return mesg, status_codes.HTTP_201_CREATED

class DeviceDetailInfo(BaseResource):
    def post(self):
        mesg = {}
        args = device_detailinfo_parser.parse_args()
        try:
            device_id = args['device_id']
            if device_id is None:
                raise KeyError('type error')
            else:
                result = self.app.get_device_reader().get_device_host_by_id(device_id)
                ret = execute_cmd("/usr/bin/env php /opt/observium/discovery.php -h %s" % (result['hostname']))
                mesg = self.app.get_device_reader().get_device_detail_by_id(device_id)
        except KeyError as e:
            raise DeviceNotExistError
        except Exception as e:
            raise AccessDatabaseError

        return mesg, status_codes.HTTP_200_OK


class DeviceNetworkInfo(BaseResource):
    def get(self, device_id):
        mesg = {}
        try:
            mesg = self.app.get_device_reader().get_device_networkinfo(device_id)

        except KeyError as e:
            raise DeviceNotExistError
        except Exception as e:
            raise AccessDatabaseError

        return mesg, status_codes.HTTP_200_OK


class DeviceArptable(BaseResource):
    def get(self, device_id):
        mesg = {}
        args = device_arp_parser.parse_args()
        try:
            mesg = self.app.get_device_reader().get_device_arptable(device_id, cur_page= args['page'], page_size=args['limit'])

        except KeyError as e:
            raise DeviceNotExistError
        except Exception as e:
            raise AccessDatabaseError

        return mesg, status_codes.HTTP_200_OK

class DeviceNeighbours(BaseResource):
    def get(self, device_id):
        mesg = {}
        try:
            mesg = self.app.get_device_reader().get_device_neighbours(device_id)

        except KeyError as e:
            raise DeviceNotExistError
        except Exception as e:
            raise AccessDatabaseError

        return mesg, status_codes.HTTP_200_OK

class DeviceFdbtable(BaseResource):
    def get(self, device_id):
        mesg = {}
        args = device_fdb_parser.parse_args()
        try:
            mesg = self.app.get_device_reader().get_device_fdbtable(device_id, cur_page= args['page'], page_size=args['limit'])

        except KeyError as e:
            raise DeviceNotExistError
        except Exception as e:
            raise AccessDatabaseError

        return mesg, status_codes.HTTP_200_OK

class DeviceVlans(BaseResource):
    def get(self, device_id):
        mesg = {}
        try:
            mesg = self.app.get_device_reader().get_device_vlans(device_id)

        except KeyError as e:
            raise DeviceNotExistError
        except Exception as e:
            raise AccessDatabaseError

        return mesg, status_codes.HTTP_200_OK

class DeviceStatusList(BaseResource):
    def get(self):
        try:
            mesg = self.app.get_device_reader().get_device_available()
        except Exception as e:
            LOG.warning('AccessDatabaseError', e)
            raise AccessDatabaseError

        return mesg, status_codes.HTTP_200_OK

class DeviceStatus(BaseResource):
    def get(self, device_id):
        try:
            mesg = self.app.get_device_reader().get_device_available_by_id(device_id)
            if mesg is None:
                raise DeviceNotExistError
        except KeyError as e:
            raise DeviceNotExistError
        except DeviceNotExistError:
            raise
        except Exception as e:
            LOG.warning('AccessDatabaseError', e)
            raise AccessDatabaseError

        return mesg, status_codes.HTTP_200_OK



#class Device
