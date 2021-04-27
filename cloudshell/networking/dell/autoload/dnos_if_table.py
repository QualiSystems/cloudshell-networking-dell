from cloudshell.snmp.autoload.snmp_if_table import SnmpIfTable

from cloudshell.networking.dell.autoload.dnos_snmp_if_port import DNOSSnmpIfPort
from cloudshell.networking.dell.autoload.dnos_snmp_if_port_channel import DNOSIfPortChannel


class DNOSIfTable(SnmpIfTable):
    IF_PORT = DNOSSnmpIfPort
    IF_PORT_CHANNEL = DNOSIfPortChannel
