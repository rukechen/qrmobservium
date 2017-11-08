from flask_restful import request, reqparse, abort, fields, marshal
from qrmobservium.resources.base_resource import BaseResource
from qrmobservium.common import status_codes
import rrdtool
import subprocess, sys

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

#class Device
