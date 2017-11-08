import logging, sys, os
import simplejson

class Application(object):

    def __init__(self, tmp=None):
        # TODO
        # - setup service member here and provide methods to access instances
        self.tmp = tmp
