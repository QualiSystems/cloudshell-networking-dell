#!/usr/bin/python
# -*- coding: utf-8 -*-


from cloudshell.devices.snmp_handler import SnmpHandler
from ftos.flows.ftos_disable_snmp_flow import FTOSDisableSnmpFlow
from ftos.flows.ftos_enable_snmp_flow import FTOSEnableSnmpFlow


class FTOSSnmpHandler(SnmpHandler):
    def __init__(self, resource_config, logger, api, cli_handler):
        super(FTOSSnmpHandler, self).__init__(resource_config, logger, api)
        self.cli_handler = cli_handler

    def _create_enable_flow(self):
        return FTOSEnableSnmpFlow(self.cli_handler, self._logger)

    def _create_disable_flow(self):
        return FTOSDisableSnmpFlow(self.cli_handler, self._logger)
