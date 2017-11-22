from flask_restful import request, reqparse, abort, fields, marshal
from qrmobservium.resources.base_resource import BaseResource
from qrmobservium.common import status_codes
from qrmobservium.common.errors import DeviceNotExistError, AccessDatabaseError
from qrmobservium.common import logger

LOG = logger.Logger(__name__)
# request
history_analysis_parser = reqparse.RequestParser()
history_analysis_parser.add_argument('start_time', type=str, location='args', required=True, help='ex: 2017-05-04 19:33:55')
history_analysis_parser.add_argument('end_time', type=str, location='args', required=True, help='ex: 2017-05-14 19:33:55')
history_analysis_parser.add_argument('metric', type=unicode, location='args', default=None)

class AnalysisSNMPHistory(BaseResource):
    def get(self, device_id, sensor_id):
        mesg = {}
        args = history_analysis_parser.parse_args()
        try:
            mesg = self.app.get_data_analysis_reader().get_snmp_health_history_data(device_id, args['metric'], sensor_id, args['start_time'], args['end_time'])
        except Exception as e:
            LOG.warning('AccessDatabaseError: '+str(e))
            raise AccessDatabaseError

        return mesg, status_codes.HTTP_200_OK


