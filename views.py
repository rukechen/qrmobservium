from flask import Flask, Blueprint, send_from_directory, make_response, request, current_app, jsonify
from flask_cors import CORS
from flask_restful import Api

from qrmobservium.resources import devices, analysis, about, live_data, event_logs, alert_logs, alert_setting
from qrmobservium.common import errors
from qrmobservium.services.application import Application

api_blueprint = Blueprint('api', __name__)

CORS(api_blueprint, resources={r"/api/*": {"origins": "*"}})

api = Api(api_blueprint, errors=errors.get_errors_defined())

qrmobservium_app = Application()
app_for_resources = {
    'application': qrmobservium_app
}

api.add_resource(about.About, '/about', resource_class_kwargs=app_for_resources)
#devices
api.add_resource(devices.DeviceDataCollecting, '/v1/devices/analysis', resource_class_kwargs=app_for_resources)
api.add_resource(devices.DeviceUpdate, '/v1/devices/update', resource_class_kwargs=app_for_resources)
api.add_resource(devices.DeviceManage, '/v1/devices/devicemgt', resource_class_kwargs=app_for_resources)
api.add_resource(devices.DeviceDetailInfo, '/v1/devices/snmpdetailinfo', resource_class_kwargs=app_for_resources)
api.add_resource(devices.DeviceSummary, '/v1/devices/summary', resource_class_kwargs=app_for_resources)
api.add_resource(devices.DeviceList, '/v1/devices', resource_class_kwargs=app_for_resources)
api.add_resource(devices.DeviceStatusList, '/v1/devices/status', resource_class_kwargs=app_for_resources)
api.add_resource(devices.DeviceStatus, '/v1/devices/status/<string:device_id>', resource_class_kwargs=app_for_resources)
api.add_resource(devices.DeviceSensors, '/v1/devices/sensors/<string:device_id>', resource_class_kwargs=app_for_resources)
api.add_resource(live_data.LiveData, '/v1/livedata/<string:device_id>/<string:metric_id>', resource_class_kwargs=app_for_resources)
api.add_resource(live_data.LiveDataSensorTable, '/v1/livedata/<string:device_id>', resource_class_kwargs=app_for_resources)

#network related
api.add_resource(devices.DeviceNetworkInfo, '/v1/devices/networkinfo/<string:device_id>', resource_class_kwargs=app_for_resources)
api.add_resource(devices.DeviceArptable, '/v1/devices/arptable/<string:device_id>', resource_class_kwargs=app_for_resources)
api.add_resource(devices.DeviceNeighbours, '/v1/devices/neighbours/<string:device_id>', resource_class_kwargs=app_for_resources)
api.add_resource(devices.DeviceFdbtable, '/v1/devices/fdbtable/<string:device_id>', resource_class_kwargs=app_for_resources)
api.add_resource(devices.DeviceVlans, '/v1/devices/vlans/<string:device_id>', resource_class_kwargs=app_for_resources)

#analysis

api.add_resource(analysis.AnalysisSNMPHistory, '/v1/analysis/snmp/<string:device_id>/<string:metric_id>', resource_class_kwargs=app_for_resources)

#eventlog
api.add_resource(event_logs.EventLogs, '/v1/eventlogs', resource_class_kwargs=app_for_resources)

#alertlog
api.add_resource(alert_logs.AlertLogs, '/v1/logs/alert', resource_class_kwargs=app_for_resources)

#alertsetting
api.add_resource(alert_setting.AlertSetting, '/v1/alert/setting', resource_class_kwargs=app_for_resources)

#alerts
api.add_resource(alert_setting.Alerts, '/v1/alerts', resource_class_kwargs=app_for_resources)


