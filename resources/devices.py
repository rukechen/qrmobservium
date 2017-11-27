from flask_restful import request, reqparse, abort, fields, marshal
from qrmobservium.resources.base_resource import BaseResource
from qrmobservium.common import status_codes
from qrmobservium.common.errors import DeviceNotExistError, AccessDatabaseError
import rrdtool
import subprocess, sys


device_mgt_parser = reqparse.RequestParser()
device_mgt_parser.add_argument('jid', type=str, location='json', required=True)
device_mgt_parser.add_argument('devices', type=list, location='json', default=[], help='devices')


device_detailinfo_parser = reqparse.RequestParser()
device_detailinfo_parser.add_argument('jid', type=str, location='json', required=True)
device_detailinfo_parser.add_argument('ip', type=str, location='json', required=True)
device_detailinfo_parser.add_argument('hostname', type=str, location='json')


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
                ret = execute_cmd("/usr/bin/env php /opt/observium/delete_device.php %s rrd" % dev['ip'])
                #print 'command result %s' % ret
        except Exception as e:
            print e

        return "", status_codes.HTTP_201_CREATED


    def post(self):
        args = device_mgt_parser.parse_args()
        devices = args['devices']
        task_msg = {
            'jid':args['jid'],
            'devices':devices,
            'task_dev_count':len(devices),
            'task_detail':'add_devices',
            'desc':'add_devices',
        }
        print 'task_mgs %s' % task_msg
        try:
            for dev in task_msg['devices']:
                #print 'dev %s %s '% (dev['ip'], dev['community'])
                ret = execute_cmd("/usr/bin/env php /opt/observium/add_device.php  %s %s" % (dev['ip'], dev['community']))
                print ret
                if 'success' in ret:
                    #get_device_detail_by_hostname
                    #device_id = self.app.get_device_reader().get_device_id_by_host(dev['ip'])
                    #if device_id is None:
                        
                    #self.app.get_device_reader().get_device_detail_by_id()
                    print 'added successfully'
                else:
                    abort(status_codes.HTTP_400_BAD_REQUEST, message="Already added")
        except Exception as e:
            print e
        #issue_device_mgt_command(self.app, task_msg)

        return "", status_codes.HTTP_201_CREATED


class DeviceDetailInfo(BaseResource):
    def post(self):
        mesg = {}
        args = device_detailinfo_parser.parse_args()
        try:
            device_id = self.app.get_device_reader().get_device_id_by_host(args['ip'])
            if device_id is None:
                raise KeyError('type error')
            else:
                ret = execute_cmd("/usr/bin/env php /opt/observium/discovery.php -h %s" % (args['ip']))
                mesg = self.app.get_device_reader().get_device_detail_by_id(device_id['device_id'])
        except KeyError as e:
            raise DeviceNotExistError 
        except Exception as e:
            raise AccessDatabaseError

        return mesg, status_codes.HTTP_200_OK

#class  





#class Device
