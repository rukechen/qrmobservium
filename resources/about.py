from base_resource import BaseResource
from flask_restful import fields, marshal
from qrmobservium.common import logger, status_codes
from qrmobservium.common.errors import UnknowExceptionError

LOG = logger.Logger(__name__)

# response
about_fields = {
    'api_version': fields.String(default='0.0.0'),
    'port': fields.String(default='4504'),
    'ip': fields.String(default='127.0.0.1'),
    'api_prefix': fields.String(default='api')
}

# resources
class About(BaseResource):

    def get(self):
        response = {}

        try:
            response['api_version'] = '1.0.0'
            response['port'] = '4504'
            response['ip'] = '127.0.0.1'
            response['api_prefix'] = 'api/v1'

        except Exception as e:
            LOG.error('About[get]', e)
            raise UnknowExceptionError

        response = marshal(response, about_fields)

        return response, status_codes.HTTP_200_OK
