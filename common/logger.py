import sys, os
import logging
import logging.handlers
from qrmobservium.common.singleton import Singleton

QRM_DEBUG = os.getenv('QRMOBSERVIUM_DEBUG', False)


class Logger(object):
    __metaclass__ = Singleton

    def __init__(self, logger_name='qrmobservium'):

        f = logging.Formatter(fmt='%(levelname)s:\t%(name)s:\t%(asctime)s %(message)s',
            datefmt="%Y-%m-%d %H:%M:%S")
        handlers = [
            logging.handlers.RotatingFileHandler('qrmobservium.log', encoding='utf8', maxBytes=5000000, backupCount=1),
            logging.StreamHandler()
        ]

        self._logger_name = logger_name;
        self._logger = logging.getLogger('qrmobservium')

        # change it to warning when production
        #logging_level = logging.WARNING
        logging_level = logging.INFO
        if QRM_DEBUG:
            logging_level = logging.DEBUG
        self._logger.setLevel(logging_level)

        for h in handlers:
            h.setFormatter(f)
            h.setLevel(logging_level)
            self._logger.addHandler(h)

    def _find_caller(self):
        """
        Find the stack frame of the caller so that we can note the source
        file name, line number and function name.
        """

        f = None
        try:
            raise Exception
        except:
            # [f_back] frame -> logger -> caller
            f = sys.exc_info()[2].tb_frame.f_back.f_back.f_back

        co = f.f_code
        filename = os.path.normcase(co.co_filename)
        rv = (filename, f.f_lineno, co.co_name)
        return rv

    def process_log(self, msg):
        fn, lno, func = self._find_caller()
        fmt = '\t%s#%s(lineno:%s)\n\t%s'
        return fmt % (fn, func, lno, msg)

    def info(self, msg):
        logmsg = self.process_log(msg)
        self._logger.info(logmsg)

    def debug(self, msg):
        logmsg = self.process_log(msg)
        self._logger.debug(logmsg)

    def warning(self, msg, error=None):
        logmsg = self.process_log(msg)
        self._logger.warning(logmsg)
        if error:
            self._logger.exception(error)

    def error(self, msg, error=None):
        logmsg = self.process_log(msg)
        self._logger.error(logmsg)
        if error:
            self._logger.exception(error)




