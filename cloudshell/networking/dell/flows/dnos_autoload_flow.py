import os

from cloudshell.networking.dell.autoload.dnos_port_attrs_service import DNOSSnmpPortAttrTables
from cloudshell.networking.dell.autoload.dnos_snmp_autoload import DNOSSNMPAutoload
from cloudshell.networking.dell.autoload.dnos_snmp_if_port import DNOSSnmpIfPort
from cloudshell.networking.dell.autoload.dnos_snmp_if_port_channel import DNOSIfPortChannel
from cloudshell.shell.flows.autoload.basic_flow import AbstractAutoloadFlow


class DNOSSnmpAutoloadFlow(AbstractAutoloadFlow):
    CISCO_MIBS_FOLDER = os.path.join(os.path.dirname(__file__), os.pardir, "../autoload", "mibs")

    def __init__(self, logger, snmp_handler):
        super(DNOSSnmpAutoloadFlow, self).__init__(logger)
        self._snmp_handler = snmp_handler

    def _autoload_flow(self, supported_os, resource_model):
        with self._snmp_handler.get_service() as snmp_service:
            snmp_service.add_mib_folder_path(self.CISCO_MIBS_FOLDER)
            snmp_service.load_mib_tables(
                ["CISCO-PRODUCTS-MIB", "CISCO-ENTITY-VENDORTYPE-OID-MIB"]
            )
            dnos_snmp_autoload = DNOSSNMPAutoload(snmp_service, self._logger)
            dnos_snmp_autoload.entity_table_service.set_port_exclude_pattern(
                r"stack|engine|management|"
                r"mgmt|voice|foreign|cpu|"
                r"control\s*ethernet\s*port|"
                r"console\s*port"
            )
            dnos_snmp_autoload.entity_table_service.set_module_exclude_pattern(
                r"powershelf|cevsfp|cevxfr|"
                r"cevxfp|cevContainer10GigBasePort|"
                r"cevModulePseAsicPlim"
            )
            (
                dnos_snmp_autoload.if_table_service.port_attributes_service
            ) = DNOSSnmpPortAttrTables(snmp_service, self._logger)
            dnos_snmp_autoload.if_table_service.if_port_type = DNOSSnmpIfPort
            dnos_snmp_autoload.if_table_service.if_port_channel_type = (
                DNOSIfPortChannel
            )
            return dnos_snmp_autoload.discover(
                supported_os, resource_model, validate_module_id_by_port_name=True
            )
