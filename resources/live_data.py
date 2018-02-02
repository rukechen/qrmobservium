from flask_restful import request, reqparse, abort, fields, marshal
from qrmobservium.resources.base_resource import BaseResource
from qrmobservium.common import status_codes
from qrmobservium.common.errors import DeviceNotExistError, AccessDatabaseError
from qrmobservium.common import logger

LOG = logger.Logger(__name__)
# request
livedata_parser = reqparse.RequestParser()
livedata_parser.add_argument('sensor_table', type=unicode, location='args', default=None)


livedatasensortable_parser = reqparse.RequestParser()
livedatasensortable_parser.add_argument('sensor_table', type=unicode, location='args', default=None)

class LiveData(BaseResource):
    def get(self, device_id, metric_id):
        mesg = {}
        args = livedata_parser.parse_args()
        try:
            mesg = self.app.get_live_data_reader().get_livedata(device_id, args['sensor_table'], metric_id)
        except KeyError as e:
            raise DeviceNotExistError
        except Exception as e:
            LOG.warning('AccessDatabaseError: '+str(e))
            raise AccessDatabaseError

        return mesg, status_codes.HTTP_200_OK

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
