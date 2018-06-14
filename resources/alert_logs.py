from flask_restful import request, reqparse, abort, fields, marshal
from qrmobservium.resources.base_resource import BaseResource
from qrmobservium.common import status_codes
from qrmobservium.common.errors import DeviceNotExistError, AccessDatabaseError
from qrmobservium.common import logger

LOG = logger.Logger(__name__)
# request
alertlogs_parser = reqparse.RequestParser()
alertlogs_parser.add_argument('device_id', type=int, location='args', default='')
alertlogs_parser.add_argument('entity_type', type=str, location='args', default='')
alertlogs_parser.add_argument('start_time', type=str, location='args', help='ex: 2017-05-04 19:33:55')
alertlogs_parser.add_argument('end_time', type=str, location='args', help='ex: 2017-05-14 19:33:55')
alertlogs_parser.add_argument('page', type=int, location='args', default=1)
alertlogs_parser.add_argument('limit', type=int, location='args', default=20)
class AlertLogs(BaseResource):
    def get(self):
        mesg = {}
        args = alertlogs_parser.parse_args()
        try:
            mesg = self.app.get_alert_log_reader().get_snmp_alertlog(device_id=args['device_id'], entity_type=args['entity_type'] ,start_time=args['start_time'], end_time=args['end_time'], cur_page=args['page'], page_size=args['limit'])
        except KeyError as e:
            raise DeviceNotExistError
        except Exception as e:
            LOG.warning('AccessDatabaseError: '+str(e))
            raise AccessDatabaseError

        return mesg, status_codes.HTTP_200_OK

