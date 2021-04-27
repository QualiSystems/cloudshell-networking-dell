#!/usr/bin/python
# -*- coding: utf-8 -*-
import re

from cloudshell.devices.flows.cli_action_flows import EnableSnmpFlow
from cloudshell.snmp.snmp_parameters import SNMPV3Parameters, SNMPV2WriteParameters
from ftos.command_actions.enable_disable_snmp_actions import EnableDisableSnmpActions


class FTOSEnableSnmpFlow(EnableSnmpFlow):
    DEFAULT_SNMP_VIEW = "quali_snmp_view"
    DEFAULT_SNMP_GROUP = "quali_snmp_group"
    SNMP_AUTH_MAP = {v: k for k, v in SNMPV3Parameters.AUTH_PROTOCOL_MAP.iteritems()}
    SNMP_PRIV_MAP = {v: k for k, v in SNMPV3Parameters.PRIV_PROTOCOL_MAP.iteritems()}

    def __init__(self, cli_handler, logger, create_group=True):
        """
        Enable snmp flow
        :param cli_handler:
        :type cli_handler: ftos.cli.ftos_cli_handler.FTOSCliHandler
        :param logger:
        :return:
        """
        super(FTOSEnableSnmpFlow, self).__init__(cli_handler, logger)

        self._cli_handler = cli_handler
        self._create_group = create_group

    def execute_flow(self, snmp_parameters):
        if hasattr(snmp_parameters, "snmp_community") and not snmp_parameters.snmp_community:
            message = 'SNMP community cannot be empty'
            self._logger.error(message)
            raise Exception(self.__class__.__name__, message)

        with self._cli_handler.enable_mode_session() as enable_session:
            snmp_actions = EnableDisableSnmpActions(enable_session, self._cli_handler.config_mode, self._logger)
            if isinstance(snmp_parameters, SNMPV3Parameters):
                self._enable_snmp_v3(snmp_parameters, snmp_actions)
            else:
                self._enable_snmp(snmp_parameters, snmp_actions)

            self._verify(snmp_parameters)

    def _enable_snmp(self, snmp_parameters, snmp_actions):
        """
        :type snmp_parameters: cloudshell.snmp.snmp_parameters.SNMPParameters
        :type snmp_actions: ftos.command_actions.enable_disable_snmp_actions.EnableDisableSnmpActions
        """

        if isinstance(snmp_parameters, SNMPV2WriteParameters):
            read_only_community = False
        else:
            read_only_community = True

        current_snmp_communities = snmp_actions.get_current_snmp_config()
        snmp_community = snmp_parameters.snmp_community
        if not re.search("snmp-server community {}".format(snmp_parameters.snmp_community),
                         current_snmp_communities):
            snmp_actions.enable_snmp(snmp_community, read_only_community)
        else:
            self._logger.debug("SNMP Community '{}' already configured".format(snmp_community))

    def _enable_snmp_v3(self, snmp_parameters, snmp_actions):
        """
        :type snmp_parameters: cloudshell.snmp.snmp_parameters.SNMPV3Parameters
        :type snmp_actions: ftos.command_actions.enable_disable_snmp_actions.EnableDisableSnmpActions
        """
        current_snmp_users = snmp_actions.get_snmp_users()
        if snmp_parameters.snmp_user not in current_snmp_users:
            self._validate_snmp_v3_params(snmp_parameters)
            if self._create_group:
                current_snmp_config = snmp_actions.get_current_snmp_config()
                if "snmp-server view {}".format(self.DEFAULT_SNMP_VIEW) not in current_snmp_config:
                    snmp_actions.enable_snmp_view(snmp_view=self.DEFAULT_SNMP_VIEW)
                if "snmp-server group {}".format(self.DEFAULT_SNMP_GROUP) not in current_snmp_config:
                    snmp_actions.enable_snmp_group(snmp_group=self.DEFAULT_SNMP_GROUP,
                                                   snmp_view=self.DEFAULT_SNMP_VIEW)
                snmp_actions.enable_snmp_v3(snmp_user=snmp_parameters.snmp_user,
                                            snmp_password=snmp_parameters.snmp_password,
                                            auth_protocol=self.SNMP_AUTH_MAP[
                                                snmp_parameters.auth_protocol].lower(),
                                            priv_protocol=self.SNMP_PRIV_MAP[
                                                snmp_parameters.private_key_protocol].lower(),
                                            snmp_priv_key=snmp_parameters.snmp_private_key,
                                            snmp_group=self.DEFAULT_SNMP_GROUP)
            else:
                priv_protocol = self.SNMP_PRIV_MAP[snmp_parameters.private_key_protocol].lower()
                if priv_protocol == "des":
                    priv_protocol = ""
                snmp_actions.enable_snmp_v3(snmp_user=snmp_parameters.snmp_user,
                                            snmp_password=snmp_parameters.snmp_password,
                                            auth_protocol=self.SNMP_AUTH_MAP[
                                                snmp_parameters.auth_protocol].lower(),
                                            priv_protocol=priv_protocol,
                                            snmp_priv_key=snmp_parameters.snmp_private_key,
                                            snmp_group=None)

    def _verify(self, snmp_parameters, snmp_actions):
        """
        :type snmp_parameters: cloudshell.snmp.snmp_parameters.SNMPParameters
        :type snmp_actions: ftos.command_actions.enable_disable_snmp_actions.EnableDisableSnmpActions
        """
        self._logger.info("Start verification of SNMP config")
        if isinstance(snmp_parameters, SNMPV3Parameters):
            updated_snmp_users = snmp_actions.get_snmp_users()
            if snmp_parameters.snmp_user not in updated_snmp_users:
                raise Exception(self.__class__.__name__, "Failed to create SNMP v3 Configuration." +
                                " Please check Logs for details")
        else:
            updated_snmp_communities = snmp_actions.get_current_snmp_config()
            if not re.search("snmp-server community {}".format(snmp_parameters.snmp_community),
                             updated_snmp_communities):
                raise Exception(self.__class__.__name__, "Failed to create SNMP community." +
                                " Please check Logs for details")

    def _validate_snmp_v3_params(self, snmp_v3_params):
        message = "Failed to enable SNMP v3: "
        error = "'{}' attribute cannot be empty"
        is_failed = False
        if not snmp_v3_params.private_key_protocol or self.SNMP_PRIV_MAP[
            snmp_v3_params.private_key_protocol] == 'No Privacy Protocol':
            # SNMP V3 Privacy Protocol
            is_failed = True
            message += (error.format("SNMP V3 Privacy Protocol") + " or set to 'No Privacy Protocol'")

        if not snmp_v3_params.auth_protocol or self.SNMP_AUTH_MAP[
            snmp_v3_params.auth_protocol] == 'No Authentication Protocol':
            # SNMP V3 Authentication Protocol
            is_failed = True
            message += (error.format("SNMP V3 Authentication Protocol") + " or set to 'No Authentication Protocol'")

        if not snmp_v3_params.snmp_user:
            is_failed = True
            message += error.format("SNMP V3 User")

        if not snmp_v3_params.snmp_private_key:
            is_failed = True
            message += error.format("SNMP V3 Private Key")

        if not snmp_v3_params.snmp_password:
            is_failed = True
            message += error.format("SNMP V3 Password")

        if is_failed:
            self._logger.error(message)
            raise AttributeError(self.__class__.__name__, message)
