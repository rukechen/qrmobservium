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
