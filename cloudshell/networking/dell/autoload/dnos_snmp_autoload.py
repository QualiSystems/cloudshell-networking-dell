#!/usr/bin/python
# -*- coding: utf-8 -*-
from cloudshell.snmp.autoload.generic_snmp_autoload import GenericSNMPAutoload

from cloudshell.networking.dell.autoload.dnos_if_table import DNOSIfTable


class DNOSSNMPAutoload(GenericSNMPAutoload):
    @property
    def if_table_service(self):
        if not self._if_table:
            self._if_table = DNOSIfTable(
                snmp_handler=self.snmp_handler, logger=self.logger
            )

        return self._if_table
