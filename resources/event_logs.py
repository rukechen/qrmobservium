from flask_restful import request, reqparse, abort, fields, marshal
from qrmobservium.resources.base_resource import BaseResource
from qrmobservium.common import status_codes
from qrmobservium.common.errors import DeviceNotExistError, AccessDatabaseError
from qrmobservium.common import logger

LOG = logger.Logger(__name__)
# request
eventlogs_parser = reqparse.RequestParser()
eventlogs_parser.add_argument('start_time', type=str, location='args', help='ex: 2017-05-04 19:33:55')
eventlogs_parser.add_argument('end_time', type=str, location='args', help='ex: 2017-05-14 19:33:55')

class EventLogs(BaseResource):
    def get(self):
        mesg = {}
        args = eventlogs_parser.parse_args()
        try:
            if args['start_time'] and args['end_time']:
                mesg = self.app.get_event_log_reader().get_eventlog(start_time=args['start_time'], end_time=args['end_time'])
            else:
                mesg = self.app.get_event_log_reader().get_eventlog()
        except KeyError as e:
            raise DeviceNotExistError
        except Exception as e:
            LOG.warning('AccessDatabaseError: '+str(e))
            raise AccessDatabaseError

        return mesg, status_codes.HTTP_200_OK

