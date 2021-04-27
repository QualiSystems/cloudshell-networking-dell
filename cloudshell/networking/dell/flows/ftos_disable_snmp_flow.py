#!/usr/bin/python
# -*- coding: utf-8 -*-
import re

from cloudshell.devices.flows.cli_action_flows import DisableSnmpFlow
from cloudshell.snmp.snmp_parameters import SNMPV3Parameters
from ftos.command_actions.enable_disable_snmp_actions import EnableDisableSnmpActions
from ftos.flows.ftos_enable_snmp_flow import FTOSEnableSnmpFlow


class FTOSDisableSnmpFlow(DisableSnmpFlow):
    def __init__(self, cli_handler, logger, remove_group=True):
        """
          Enable snmp flow
          :param cli_handler:
            :type cli_handler: ftos.cli.ftos_cli_handler.FTOSCliHandler
          :param logger:
          :return:
          """
        super(FTOSDisableSnmpFlow, self).__init__(cli_handler, logger)
        self._cli_handler = cli_handler
        self._remove_group = remove_group

    def execute_flow(self, snmp_parameters=None):
        with self._cli_handler.enable_mode_session() as enable_sesion:
            snmp_actions = EnableDisableSnmpActions(enable_sesion, self._cli_handler.config_mode, self._logger)
            if isinstance(snmp_parameters, SNMPV3Parameters):
                self._disable_snmp_v3(snmp_parameters, snmp_actions)
            else:
                self._disable_snmp(snmp_parameters, snmp_actions)

    def _disable_snmp_v3(self, snmp_parameters, snmp_actions):
        """
        :type snmp_parameters: cloudshell.snmp.snmp_parameters.SNMPV3Parameters
        :type snmp_actions: ftos.command_actions.enable_disable_snmp_actions.EnableDisableSnmpActions
        """
        current_snmp_users = snmp_actions.get_snmp_users()
        if snmp_parameters.snmp_user in current_snmp_users:
            if self._remove_group:
                snmp_actions.remove_snmp_user(snmp_parameters.snmp_user, FTOSEnableSnmpFlow.DEFAULT_SNMP_GROUP)
                current_snmp_config = snmp_actions.get_current_snmp_config()
                groups = re.findall(FTOSEnableSnmpFlow.DEFAULT_SNMP_GROUP, current_snmp_users)
                if len(groups) < 2:
                    snmp_actions.remove_snmp_group(FTOSEnableSnmpFlow.DEFAULT_SNMP_GROUP)
                    if "snmp-server view {}".format(
                            FTOSEnableSnmpFlow.DEFAULT_SNMP_VIEW) in current_snmp_config:
                        snmp_actions.remove_snmp_view(FTOSEnableSnmpFlow.DEFAULT_SNMP_VIEW)
            else:
                snmp_actions.remove_snmp_user(snmp_parameters.snmp_user)

    def _disable_snmp(self, snmp_parameters, snmp_actions):
        """
        :type snmp_parameters: cloudshell.snmp.snmp_parameters.SNMPParameters
        :type snmp_actions: ftos.command_actions.enable_disable_snmp_actions.EnableDisableSnmpActions
        """
        self._logger.debug("Start Disable SNMP")
        snmp_actions.disable_snmp(snmp_parameters.snmp_community)

    def _verify(self, snmp_parameters, snmp_actions):
        """
        :type snmp_parameters: cloudshell.snmp.snmp_parameters.SNMPParameters
        :type snmp_actions: ftos.command_actions.enable_disable_snmp_actions.EnableDisableSnmpActions
        """
        if isinstance(snmp_parameters, SNMPV3Parameters):
            updated_snmp_users = snmp_actions.get_snmp_users()
            if snmp_parameters.snmp_user in updated_snmp_users:
                raise Exception(self.__class__.__name__, "Failed to remove SNMP v3 Configuration." +
                                " Please check Logs for details")
        else:
            updated_snmp_communities = snmp_actions.get_current_snmp_config()
            if re.search("snmp-server community {}".format(snmp_parameters.snmp_community),
                         updated_snmp_communities):
                raise Exception(self.__class__.__name__, "Failed to remove SNMP community." +
                                "Please check Logs for details")
