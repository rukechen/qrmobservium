from flask_restful import request, reqparse, abort, fields, marshal
from qrmobservium.resources.base_resource import BaseResource
from qrmobservium.common import status_codes
from qrmobservium.common.errors import DeviceNotExistError, AccessDatabaseError, UnknowExceptionError
from qrmobservium.common import logger

LOG = logger.Logger(__name__)
# request
get_alert_settings_parser = reqparse.RequestParser()
get_alert_settings_parser.add_argument('page', type=int, location='args', default=1)
get_alert_settings_parser.add_argument('limit', type=int, location='args', default=50)


def delete_alert_settings_type(value):
    try:
        for delete_alert_setting in value:
            if not delete_alert_setting.get('alert_setting_id', None):
                raise ValueError("Invalid object")

    except ValueError:
        raise
    except:
        raise ValueError

    return value
delete_alert_settings_parser = reqparse.RequestParser()
delete_alert_settings_parser.add_argument('delete_alert_settings', type=delete_alert_settings_type, location='json', required=True)

def add_alert_settings_type(value):

    try:
        for add_alert_setting in value:
            devices = add_alert_setting.get('devices', None)
            if devices is None or len(devices)==0 \
            or add_alert_setting.get('alert_name', None) is None \
            or add_alert_setting.get('alert_message', None) is None \
            or add_alert_setting.get('alert_type', None) is None \
            or add_alert_setting.get('entity_attribute', None) is None \
            or add_alert_setting.get('condition_metric', None) is None \
            or add_alert_setting.get('condition_symbol', None) is None \
            or add_alert_setting.get('condition_value', None) is None \
            or add_alert_setting.get('entity_type', None) is None:
                raise ValueError("Invalid object")

            for device in devices:
                if device.get('device_id') is None:
                    raise ValueError("Invalid object")

    except ValueError:
        raise
    except:
        raise ValueError

    return value

add_alert_settings_parser = reqparse.RequestParser()
add_alert_settings_parser.add_argument('add_alert_settings', type=add_alert_settings_type, location='json', required=True)

def update_alert_settings_type(value):
    try:
        for update_alert_setting in value:

            devices = update_alert_setting.get('devices', [])
            for device in devices:
                if device.get('device_id') is None:
                    raise ValueError("Invalid object")

            if update_alert_setting.get('alert_setting_id', None) is None \
            or not 'condition_symbol' in update_alert_setting \
            or not 'condition_value' in update_alert_setting \
            or not 'condition_metric' in update_alert_setting \
            or update_alert_setting.get('alert_name', None) is None \
            or update_alert_setting.get('alert_message', None) is None:
                raise ValueError("Invalid object")

    except ValueError:
        raise
    except:
        raise ValueError

    return value

update_alert_settings_parser = reqparse.RequestParser()
update_alert_settings_parser.add_argument('update_alert_settings', type=update_alert_settings_type, location='json', required=True)

class AlertSetting(BaseResource):
    def get(self):
        mesg = {}
        args = get_alert_settings_parser.parse_args()
        try:
            mesg = self.app.get_alert_setting_reader().get_alert_settings(cur_page=args['page'], page_size=args['limit'])
        except KeyError as e:
            raise DeviceNotExistError
        except Exception as e:
            LOG.warning('AccessDatabaseError: '+str(e))
            raise AccessDatabaseError

        return mesg, status_codes.HTTP_200_OK
    def delete(self):
        delete_alert_settings_data = delete_alert_settings_parser.parse_args()
        try:
            self.app.get_alert_setting_writer().delete_alert_settings(delete_alert_settings_data['delete_alert_settings'])

        except Exception as exception:
            LOG.warning('delete alert settings fail', exception)
            raise UnknowExceptionError

        return '', status_codes.HTTP_200_OK

    def post(self):
        add_alert_settings_data = add_alert_settings_parser.parse_args()
        if len(add_alert_settings_data['add_alert_settings']) != 1:
            raise InvalidParametersError

        try:
            self.app.get_alert_setting_writer().add_alert_setting(add_alert_settings_data['add_alert_settings'][0])
            self.app.get_alert_setting_writer().update_device_alert_table()

        except Exception as exception:
            LOG.warning('add alert settings fail', exception)
            raise UnknowExceptionError

        return '', status_codes.HTTP_200_OK
    def put(self):
        update_alert_settings_data = update_alert_settings_parser.parse_args()

        if len(update_alert_settings_data['update_alert_settings']) != 1:
            raise InvalidParametersError

        try:
            self.app.get_alert_setting_writer().update_alert_setting(update_alert_settings_data['update_alert_settings'][0])

        except Exception as exception:
            LOG.warning('update alert settings fail', exception)
            raise UnknowExceptionError

        return '', status_codes.HTTP_200_OK
get_alerts_parser = reqparse.RequestParser()
get_alerts_parser.add_argument('device_id', type=int, location='args', default=None)
get_alerts_parser.add_argument('alert_status', type=int, location='args', default=0)
get_alerts_parser.add_argument('entity_type', type=str, location='args', default=None)
get_alerts_parser.add_argument('order_by', type=str, location='args', default='last_alerted')
class Alerts(BaseResource):
    def get(self):
        mesg = {}
        args = get_alerts_parser.parse_args()
        try:
            mesg = self.app.get_alert_setting_reader().get_alerts(device_id=args['device_id'], entity_type= args['entity_type'], alert_status=args['alert_status'], order_by=args['order_by'])
        except KeyError as e:
            raise DeviceNotExistError
        except Exception as e:
            LOG.warning('AccessDatabaseError: '+str(e))
            raise AccessDatabaseError

        return mesg, status_codes.HTTP_200_OK
