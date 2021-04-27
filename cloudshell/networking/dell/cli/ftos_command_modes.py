#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.cli.command_mode import CommandMode


class FTOSCommandMode(CommandMode):
    PROMPT = ''
    ENTER_COMMAND = ''
    EXIT_COMMAND = ''

    def __init__(self, prompt=None, enter_command=None, exit_command=None, enter_action_map=None, exit_action_map=None,
                 enter_error_map=None, exit_error_map=None):
        super(FTOSCommandMode, self).__init__(prompt or self.PROMPT,
                                              enter_command=enter_command or self.ENTER_COMMAND,
                                              exit_command=exit_command or self.EXIT_COMMAND,
                                              enter_action_map=enter_action_map,
                                              exit_action_map=exit_action_map,
                                              enter_error_map=enter_error_map,
                                              exit_error_map=exit_error_map)


class DefaultCommandMode(FTOSCommandMode):
    PROMPT = r'^.+>\s*$'
    ENTER_COMMAND = ''
    EXIT_COMMAND = ''

    def __init__(self, resource_config, api):
        super(DefaultCommandMode, self).__init__()
        self.resource_config = resource_config
        self._api = api


class EnableCommandMode(FTOSCommandMode):
    PROMPT = r'^.+#\s*$'
    ENTER_COMMAND = 'enable'
    EXIT_COMMAND = ''

    def __init__(self, resource_config, api):
        self.resource_config = resource_config
        self._api = api
        self._enable_password = None
        super(EnableCommandMode, self).__init__(enter_action_map=self.enter_action_map())

    def enable_password(self):
        if not self._enable_password:
            password = self.resource_config.enable_password
            self._enable_password = self._api.DecryptPassword(password).Value
        return self._enable_password

    def enter_action_map(self):
        return {"[Pp]assword": lambda session, logger: session.send_line(self.enable_password(), logger)}


class ConfigCommandMode(FTOSCommandMode):
    PROMPT = r'^.*\(conf.*\)#\s*$'
    ENTER_COMMAND = 'configure terminal'
    EXIT_COMMAND = "exit"

    def __init__(self, resource_config, api):
        self.resource_config = resource_config
        self._api = api
        super(ConfigCommandMode, self).__init__()


CommandMode.RELATIONS_DICT = {
    DefaultCommandMode: {
        EnableCommandMode: {
            ConfigCommandMode: {}
        }
    }
}


# Detached command modes

class InterfaceConfigCommandMode(FTOSCommandMode):
    PROMPT = '^.*\(conf-if-.+\)#\s*$'
    ENTER_COMMAND_TEMPLATE = 'interface {}'
    EXIT_COMMAND = 'exit'

    def __init__(self, interface_name):
        super(InterfaceConfigCommandMode, self).__init__(
            enter_command=self.ENTER_COMMAND_TEMPLATE.format(interface_name))


class VlanConfigCommandMode(InterfaceConfigCommandMode):
    ENTER_COMMAND_TEMPLATE = 'interface vlan {}'

    def __init__(self, vlan_id):
        super(InterfaceConfigCommandMode, self).__init__(
            enter_command=self.ENTER_COMMAND_TEMPLATE.format(vlan_id))


class PCConfigCommandMode(InterfaceConfigCommandMode):
    ENTER_COMMAND_TEMPLATE = 'interface port-channel {}'

    def __init__(self, port_channel_id):
        super(InterfaceConfigCommandMode, self).__init__(
            enter_command=self.ENTER_COMMAND_TEMPLATE.format(port_channel_id))
