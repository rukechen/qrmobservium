import logging, sys, os
import simplejson


from qrmobservium.persistent import interfaces

class Application(object):

    def __init__(self, tmp=None):
        # TODO
        # - setup service member here and provide methods to access instances
        self.tmp = tmp
    @classmethod
    def get_device_reader(cls):
        return interfaces.DeviceReader()
    @classmethod
    def get_data_analysis_reader(cls):
        return interfaces.DataAnalysisReader()
    @classmethod
    def get_live_data_reader(cls):
        return interfaces.LiveDataReader()
    @classmethod
    def get_event_log_reader(cls):
        return interfaces.EventLogReader()
