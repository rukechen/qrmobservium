from flask import Flask, Blueprint, send_from_directory, make_response, request, current_app, jsonify
from flask_cors import CORS
from flask_restful import Api

from qrmobservium.resources import devices, analysis, about
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
api.add_resource(devices.DeviceDataCollecting, '/v1/devices/analysis', resource_class_kwargs=app_for_resources)
api.add_resource(devices.DeviceUpdate, '/v1/devices/update', resource_class_kwargs=app_for_resources)
api.add_resource(devices.DeviceManage, '/v1/devices/devicemgt', resource_class_kwargs=app_for_resources)
api.add_resource(devices.DeviceDetailInfo, '/v1/devices/snmpdetailinfo', resource_class_kwargs=app_for_resources)

#network related
api.add_resource(devices.DeviceNetworkInfo, '/v1/devices/networkinfo/<string:device_id>', resource_class_kwargs=app_for_resources)
api.add_resource(devices.DeviceArptable, '/v1/devices/arptable/<string:device_id>', resource_class_kwargs=app_for_resources)
api.add_resource(devices.DeviceNeighbours, '/v1/devices/neighbours/<string:device_id>', resource_class_kwargs=app_for_resources)
api.add_resource(devices.DeviceFdbtable, '/v1/devices/fdbtable/<string:device_id>', resource_class_kwargs=app_for_resources)
#analysis

api.add_resource(analysis.AnalysisSNMPHistory, '/v1/analysis/snmp/<string:device_id>/<string:metric_id>', resource_class_kwargs=app_for_resources)
