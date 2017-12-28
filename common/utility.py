import datetime
from netaddr import IPNetwork, IPAddress
from netaddr.core import AddrFormatError
from qrmobservium.common import logger

LOG = logger.Logger(__name__)



def is_valid_ip_address(address):
    is_network = True if len(address.split('/')) > 1 else False
    try:
        if is_network:
            IPNetwork(address)
        else:
            IPAddress(address)
    except AddrFormatError as e:
        LOG.warning('invalid ip address', e)
        return False

    return True
