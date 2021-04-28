#!/usr/bin/python
# -*- coding: utf-8 -*-
import re

import cloudshell.networking.dell.command_templates.enable_disable_snmp as enable_disable_snmp
from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor
from cloudshell.networking.dell.cli.dnos_command_modes import EnableCommandMode


class EnableDisableSnmpActions(object):
    READ_ONLY = "ro"
    READ_WRITE = "rw"

    def __init__(self, cli_service, config_mode, logger):
        """
        SNMP actions
        :param cli_service: config mode cli service
        :type cli_service: cloudshell.cli.cli_service_impl.CliServiceImpl
        :param logger:
        :type logger: Logger
        :return:
        """
        if not isinstance(cli_service.command_mode, EnableCommandMode):
            raise TypeError(self.__class__.__name__, 'Incorrect cli service command mode')
        self._cli_service = cli_service
        self._logger = logger
        self._config_mode = config_mode

    def get_current_snmp_communities(self, action_map=None, error_map=None):
        """Retrieve current snmp communities

        :param action_map: actions will be taken during executing commands, i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands, i.e. handles Invalid Commands errors
        :return:
        """

        return CommandTemplateExecutor(cli_service=self._cli_service,
                                       command_template=enable_disable_snmp.SHOW_SNMP_COMMUNITY,
                                       action_map=action_map,
                                       error_map=error_map).execute_command()

    def get_current_snmp_config(self, action_map=None, error_map=None):
        """Retrieve current snmp communities

        :param action_map: actions will be taken during executing commands, i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands, i.e. handles Invalid Commands errors
        :return:
        """

        return CommandTemplateExecutor(cli_service=self._cli_service,
                                       command_template=enable_disable_snmp.SHOW_SNMP_CONFIG,
                                       action_map=action_map,
                                       error_map=error_map).execute_command()

    def get_snmp_users(self, action_map=None, error_map=None):
        """Retrieve current snmp communities

        :param action_map: actions will be taken during executing commands, i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands, i.e. handles Invalid Commands errors
        :return:
        """

        output = CommandTemplateExecutor(cli_service=self._cli_service,
                                         command_template=enable_disable_snmp.SHOW_SNMP_USERS,
                                         action_map=action_map,
                                         error_map=error_map).execute_command()
        return re.findall(r'^user\sname\s*:\s*(\w+)\s*$', output, flags=re.IGNORECASE | re.MULTILINE)

    def enable_snmp(self, snmp_community, is_read_only_community=True, action_map=None, error_map=None):
        """Enable SNMP on the device

        :param snmp_community: community name
        :param action_map: actions will be taken during executing commands, i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands, i.e. handles Invalid Commands errors
        """

        read_only = self.READ_WRITE
        if is_read_only_community:
            read_only = self.READ_ONLY
        with self._cli_service.enter_mode(self._config_mode):
            return CommandTemplateExecutor(cli_service=self._cli_service,
                                           command_template=enable_disable_snmp.ENABLE_SNMP,
                                           action_map=action_map,
                                           error_map=error_map).execute_command(snmp_community=snmp_community,
                                                                                read_only=read_only)

    def enable_snmp_view(self, snmp_view, action_map=None, error_map=None):
        """Enable SNMP view on the device

        :param snmp_view: snmp view name
        :param action_map: actions will be taken during executing commands, i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands, i.e. handles Invalid Commands errors
        """

        with self._cli_service.enter_mode(self._config_mode) as config_mode_service:
            return CommandTemplateExecutor(cli_service=config_mode_service,
                                           command_template=enable_disable_snmp.ENABLE_SNMP_VIEW,
                                           action_map=action_map,
                                           error_map=error_map).execute_command(snmp_view=snmp_view)

    def enable_snmp_group(self, snmp_group, snmp_view, action_map=None, error_map=None):
        """Enable SNMP group on the device

        :param snmp_group: snmp group name
        :param snmp_view: snmp view name
        :param action_map: actions will be taken during executing commands, i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands, i.e. handles Invalid Commands errors
        """

        with self._cli_service.enter_mode(self._config_mode) as config_mode_service:
            return CommandTemplateExecutor(cli_service=config_mode_service,
                                           command_template=enable_disable_snmp.ENABLE_SNMP_GROUP,
                                           action_map=action_map,
                                           error_map=error_map).execute_command(snmp_group=snmp_group,
                                                                                snmp_view=snmp_view)

    def enable_snmp_v3(self, snmp_user, snmp_password, auth_protocol, snmp_priv_key, priv_protocol, snmp_group,
                       action_map=None, error_map=None):

        """Enable SNMP user on the device

        :param snmp_user: snmp user
        :param snmp_password: snmp password
        :param snmp_priv_key: snmp priv key
        :param snmp_group: snmp group name
        :param action_map: actions will be taken during executing commands, i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands, i.e. handles Invalid Commands errors
        """

        with self._cli_service.enter_mode(self._config_mode) as config_mode_service:
            if snmp_group:
                result = CommandTemplateExecutor(cli_service=config_mode_service,
                                                 command_template=enable_disable_snmp.ENABLE_SNMP_V3_WITH_GROUP,
                                                 action_map=action_map,
                                                 error_map=error_map).execute_command(snmp_user=snmp_user,
                                                                                      snmp_password=snmp_password,
                                                                                      auth_protocol=auth_protocol,
                                                                                      snmp_priv_key=snmp_priv_key,
                                                                                      priv_protocol=priv_protocol,
                                                                                      snmp_group=snmp_group)
            else:
                result = CommandTemplateExecutor(cli_service=config_mode_service,
                                                 command_template=enable_disable_snmp.ENABLE_SNMP_USER,
                                                 action_map=action_map,
                                                 error_map=error_map).execute_command(snmp_user=snmp_user,
                                                                                      snmp_password=snmp_password,
                                                                                      auth_protocol=auth_protocol,
                                                                                      snmp_priv_key=snmp_priv_key,
                                                                                      priv_protocol=priv_protocol)
            return result

    def disable_snmp(self, snmp_community, is_read_only_community=True, action_map=None, error_map=None):
        """Disable SNMP community on the device

        :param snmp_community: community name
        :param action_map: actions will be taken during executing commands, i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands, i.e. handles Invalid Commands errors
        """

        read_only = self.READ_WRITE
        if is_read_only_community:
            read_only = self.READ_ONLY
        with self._cli_service.enter_mode(self._config_mode):
            return CommandTemplateExecutor(cli_service=self._cli_service,
                                           command_template=enable_disable_snmp.DISABLE_SNMP_COMMUNITY,
                                           action_map=action_map,
                                           error_map=error_map).execute_command(snmp_community=snmp_community,
                                                                                read_only=read_only)

    def remove_snmp_group(self, snmp_group, action_map=None, error_map=None):
        """Disable SNMP community on the device

        :param snmp_group: community name
        :param action_map: actions will be taken during executing commands, i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands, i.e. handles Invalid Commands errors
        """

        return CommandTemplateExecutor(cli_service=self._cli_service,
                                       command_template=enable_disable_snmp.DISABLE_SNMP_GROUP,
                                       action_map=action_map,
                                       error_map=error_map).execute_command(snmp_group=snmp_group)

    def remove_snmp_view(self, snmp_view, action_map=None, error_map=None):
        """Disable SNMP view on the device

        :param snmp_view: community name
        :param action_map: actions will be taken during executing commands, i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands, i.e. handles Invalid Commands errors
        """

        return CommandTemplateExecutor(cli_service=self._cli_service,
                                       command_template=enable_disable_snmp.DISABLE_SNMP_VIEW,
                                       action_map=action_map,
                                       error_map=error_map).execute_command(snmp_view=snmp_view)

    def remove_snmp_user(self, snmp_user, snmp_group=None, action_map=None, error_map=None):
        """Disable SNMP user on the device

        :param snmp_user: snmp v3 user name
        :param action_map: actions will be taken during executing commands, i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands, i.e. handles Invalid Commands errors
        """

        if snmp_group:
            result = CommandTemplateExecutor(cli_service=self._cli_service,
                                             command_template=enable_disable_snmp.DISABLE_SNMP_USER_WITH_GROUP,
                                             action_map=action_map,
                                             error_map=error_map).execute_command(snmp_user=snmp_user,
                                                                                  snmp_group=snmp_group)
        else:
            result = CommandTemplateExecutor(cli_service=self._cli_service,
                                             command_template=enable_disable_snmp.DISABLE_SNMP_USER,
                                             action_map=action_map,
                                             error_map=error_map).execute_command(snmp_user=snmp_user)
        return result
