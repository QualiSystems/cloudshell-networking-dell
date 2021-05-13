import re

from cloudshell.snmp.snmp_configurator import EnableDisableSnmpFlowInterface
from cloudshell.snmp.snmp_parameters import SNMPWriteParameters, SNMPV3Parameters

from cloudshell.networking.dell.command_actions.enable_disable_snmp_actions import EnableDisableSnmpActions


class DNOSEnableDisableSNMPFlow(EnableDisableSnmpFlowInterface):
    DEFAULT_SNMP_VIEW = "quali_snmp_view"
    DEFAULT_SNMP_GROUP = "quali_snmp_group"

    # SNMP_AUTH_MAP = {v: k for k, v in SNMPV3Parameters.AUTH_PROTOCOL_MAP.iteritems()}
    # SNMP_PRIV_MAP = {v: k for k, v in SNMPV3Parameters.PRIV_PROTOCOL_MAP.iteritems()}

    def __init__(self, cli_configurator, logger):
        """Enable Disable snmp flow.

        :param cloudshell.networking.dell.cli.dnos_cli_configurator.DNOSCliConfigurator cli_configurator:
        :param logging.Logger logger:
        """
        self._cli_configurator = cli_configurator
        self._logger = logger
        self._create_group = True

    def enable_snmp(self, snmp_parameters):
        with self._cli_configurator.enable_mode_service() as cli_service:
            snmp_actions = EnableDisableSnmpActions(cli_service, self._cli_configurator.config_mode, self._logger)

            if isinstance(snmp_parameters, SNMPV3Parameters):
                self._enable_snmp_v3(snmp_actions, snmp_parameters)
            else:
                self._enable_snmp(snmp_actions, snmp_parameters)

            self._verify_enable(snmp_actions, snmp_parameters)

    def _enable_snmp(self, snmp_actions, snmp_parameters):
        """Enable SNMPv1,2.

        :param cloudshell.networking.dell.command_actions.enable_disable_snmp_actions.EnableDisableSnmpActions snmp_actions:
        :param cloudshell.snmp.snmp_parameters.SnmpParameters snmp_parameters:
        """
        if isinstance(snmp_parameters, SNMPWriteParameters):
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

    def _enable_snmp_v3(self, snmp_actions, snmp_parameters):
        """
        :param cloudshell.networking.dell.command_actions.enable_disable_snmp_actions.EnableDisableSnmpActions snmp_actions:
        :param cloudshell.snmp.snmp_parameters.SNMPV3Parameters snmp_parameters:
        """
        # current_snmp_users = snmp_actions.get_snmp_users()
        current_snmp_users = ""
        if snmp_parameters.snmp_user not in current_snmp_users:
            # self._validate_snmp_v3_params(snmp_parameters)
            if self._create_group:
                current_snmp_config = snmp_actions.get_current_snmp_config()
                if "snmp-server view {}".format(self.DEFAULT_SNMP_VIEW) not in current_snmp_config:
                    snmp_actions.enable_snmp_view(snmp_view=self.DEFAULT_SNMP_VIEW)
                if "snmp-server group {}".format(self.DEFAULT_SNMP_GROUP) not in current_snmp_config:
                    snmp_actions.enable_snmp_group(snmp_group=self.DEFAULT_SNMP_GROUP,
                                                   snmp_view=self.DEFAULT_SNMP_VIEW)
                snmp_actions.enable_snmp_v3(snmp_user=snmp_parameters.snmp_user,
                                            snmp_password=snmp_parameters.snmp_password,
                                            auth_protocol=snmp_parameters.snmp_auth_protocol.lower(),
                                            priv_protocol=snmp_parameters.snmp_private_key_protocol.lower(),
                                            snmp_priv_key=snmp_parameters.snmp_private_key,
                                            snmp_group=self.DEFAULT_SNMP_GROUP)
            else:
                priv_protocol = snmp_parameters.snmp_private_key_protocol.lower()
                if priv_protocol == "des":
                    priv_protocol = ""
                snmp_actions.enable_snmp_v3(snmp_user=snmp_parameters.snmp_user,
                                            snmp_password=snmp_parameters.snmp_password,
                                            auth_protocol=snmp_parameters.snmp_auth_protocol.lower(),
                                            priv_protocol=priv_protocol,
                                            snmp_priv_key=snmp_parameters.snmp_private_key,
                                            snmp_group=None)

    def _verify_enable(self, snmp_actions, snmp_parameters):
        """
        :param cloudshell.networking.dell.command_actions.enable_disable_snmp_actions.EnableDisableSnmpActions snmp_actions:
        :param cloudshell.snmp.snmp_parameters.SNMPV3Parameters snmp_parameters:
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

    # def _validate_snmp_v3_params(self, snmp_v3_params):
    #     message = "Failed to enable SNMP v3: "
    #     error = "'{}' attribute cannot be empty"
    #     is_failed = False
    #     if not snmp_v3_params.private_key_protocol or self.SNMP_PRIV_MAP[
    #         snmp_v3_params.private_key_protocol] == 'No Privacy Protocol':
    #         # SNMP V3 Privacy Protocol
    #         is_failed = True
    #         message += (error.format("SNMP V3 Privacy Protocol") + " or set to 'No Privacy Protocol'")
    #
    #     if not snmp_v3_params.auth_protocol or self.SNMP_AUTH_MAP[
    #         snmp_v3_params.auth_protocol] == 'No Authentication Protocol':
    #         # SNMP V3 Authentication Protocol
    #         is_failed = True
    #         message += (error.format("SNMP V3 Authentication Protocol") + " or set to 'No Authentication Protocol'")
    #
    #     if not snmp_v3_params.snmp_user:
    #         is_failed = True
    #         message += error.format("SNMP V3 User")
    #
    #     if not snmp_v3_params.snmp_private_key:
    #         is_failed = True
    #         message += error.format("SNMP V3 Private Key")
    #
    #     if not snmp_v3_params.snmp_password:
    #         is_failed = True
    #         message += error.format("SNMP V3 Password")
    #
    #     if is_failed:
    #         self._logger.error(message)
    #         raise AttributeError(self.__class__.__name__, message)

    def disable_snmp(self, snmp_parameters):
        with self._cli_configurator.enable_mode_service() as cli_service:
            snmp_actions = EnableDisableSnmpActions(cli_service, self._cli_configurator.config_mode, self._logger)
            if isinstance(snmp_parameters, SNMPV3Parameters):
                self._disable_snmp_v3(snmp_actions, snmp_parameters)
            else:
                self._disable_snmp(snmp_actions, snmp_parameters)
            self._verify_disable(snmp_parameters, snmp_actions)

    def _disable_snmp_v3(self, snmp_actions, snmp_parameters):
        """
        :param cloudshell.networking.dell.command_actions.enable_disable_snmp_actions.EnableDisableSnmpActions snmp_actions:
        :param cloudshell.snmp.snmp_parameters.SNMPV3Parameters snmp_parameters:
        """
        current_snmp_users = snmp_actions.get_snmp_users()
        if snmp_parameters.snmp_user in current_snmp_users:
            if self._remove_group:
                snmp_actions.remove_snmp_user(snmp_parameters.snmp_user, self.DEFAULT_SNMP_GROUP)
                current_snmp_config = snmp_actions.get_current_snmp_config()
                groups = re.findall(self.DEFAULT_SNMP_GROUP, current_snmp_users)
                if len(groups) < 2:
                    snmp_actions.remove_snmp_group(self.DEFAULT_SNMP_GROUP)
                    if "snmp-server view {}".format(
                            self.DEFAULT_SNMP_VIEW) in current_snmp_config:
                        snmp_actions.remove_snmp_view(self.DEFAULT_SNMP_VIEW)
            else:
                snmp_actions.remove_snmp_user(snmp_parameters.snmp_user)

    def _disable_snmp(self, snmp_actions, snmp_parameters):
        """
        :param cloudshell.networking.dell.command_actions.enable_disable_snmp_actions.EnableDisableSnmpActions snmp_actions:
        :param cloudshell.snmp.snmp_parameters.SnmpParameters snmp_parameters:
        """
        self._logger.debug("Start Disable SNMP")
        if isinstance(snmp_parameters, SNMPWriteParameters):
            read_only_community = False
        else:
            read_only_community = True
        snmp_actions.disable_snmp(snmp_parameters.snmp_community, read_only_community)

    def _verify_disable(self, snmp_parameters, snmp_actions):
        """
        :param cloudshell.networking.dell.command_actions.enable_disable_snmp_actions.EnableDisableSnmpActions snmp_actions:
        :param cloudshell.snmp.snmp_parameters.SnmpParameters snmp_parameters:
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
