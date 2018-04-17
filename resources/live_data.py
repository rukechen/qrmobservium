from flask_restful import request, reqparse, abort, fields, marshal
from qrmobservium.resources.base_resource import BaseResource
from qrmobservium.common import status_codes
from qrmobservium.common.errors import DeviceNotExistError, AccessDatabaseError
from qrmobservium.common import logger
import json,os
LOG = logger.Logger(__name__)
# request
livedata_parser = reqparse.RequestParser()
livedata_parser.add_argument('sensor_table', type=unicode, location='args', default=None)


livedatasensortable_parser = reqparse.RequestParser()
livedatasensortable_parser.add_argument('sensor_table', type=unicode, location='args', default=None)

JOBDIR = "/opt/observium/qrmobservium/common/scheduler/jobs/livedata"


def extract_livedata_values(device_id, metric_id):
    mesg = {}
    if not os.path.isdir(JOBDIR + "/" + device_id):
        if not os.path.isdir(JOBDIR + "/" + device_id):
            os.makedirs(JOBDIR + "/" + device_id)
    if not os.path.isfile(JOBDIR + "/" + device_id + "/" + metric_id):
        open(JOBDIR + "/" + device_id + "/" + metric_id, 'a').close()
        return '', status_codes.HTTP_201_CREATED
    try:
        with open( JOBDIR + "/" + device_id + "/" + "%s" % metric_id , 'r') as f:
            data = json.load(f)
        if not 'if_in' in data or not 'if_out' in data or not 'last_in' in data or not 'last_out' in data:
            return '', status_codes.HTTP_201_CREATED
        else:
            mesg['time'] = data['current_time']
            metrics = {}
            value = {}
            value['in'] = (int(data['if_in']) - int(data['last_in'])) / (int(data['current_time']) - int(data['last_time']))
            value['out'] = (int(data['if_out']) - int(data['last_out'])) / (int(data['current_time']) - int(data['last_time']))
            metrics['value'] = value
            metrics['metric_id'] = metric_id
            mesg['metrics'] = metrics
            mesg = [mesg]
    except:
        return '', status_codes.HTTP_201_CREATED
    return mesg, status_codes.HTTP_200_OK

def delete_livedata_job(device_id, metric_id):
    if not os.path.isdir(JOBDIR + "/" + device_id):
        return '', status_codes.HTTP_200_OK
    if not os.path.isfile(JOBDIR + "/" + device_id + "/" + metric_id):
        return '', status_codes.HTTP_200_OK
    else:
        os.remove(JOBDIR + "/" + device_id + "/" + metric_id)

    if len(os.listdir(JOBDIR + "/" + device_id)) <=0:
        os.rmdir(JOBDIR + "/" + device_id)
    return '', status_codes.HTTP_200_OK

class LiveData(BaseResource):
    def get(self, device_id, metric_id):
        mesg = {}
        args = livedata_parser.parse_args()
        try:
            if args['sensor_table'] == 'port':
                return extract_livedata_values(device_id, metric_id)
            else:
                mesg = self.app.get_live_data_reader().get_livedata(device_id, args['sensor_table'], metric_id)
        except KeyError as e:
            raise DeviceNotExistError
        except Exception as e:
            LOG.warning('AccessDatabaseError: '+str(e))
            raise AccessDatabaseError

        return mesg, status_codes.HTTP_200_OK
    def delete(self, device_id, metric_id):
        mesg = {}
        args = livedata_parser.parse_args()
        try:
            if args['sensor_table'] == 'port':
                return delete_livedata_job(device_id, metric_id)
            else:
                return '', status_codes.HTTP_200_OK
        except KeyError as e:
            raise DeviceNotExistError
        except Exception as e:
            LOG.warning('AccessDatabaseError: '+str(e))
            raise AccessDatabaseError
        return '', status_codes.HTTP_200_OK

class LiveDataSensorTable(BaseResource):
    def get(self, device_id):
        mesg = {}
        args = livedatasensortable_parser.parse_args()
        print args
        try:
            mesg = self.app.get_live_data_reader().get_livedata_by_sensor_table(device_id, args['sensor_table'])
        except KeyError as e:
            raise DeviceNotExistError
        except Exception as e:
            LOG.warning('AccessDatabaseError: '+str(e))
            raise AccessDatabaseError

        return mesg, status_codes.HTTP_200_OK
