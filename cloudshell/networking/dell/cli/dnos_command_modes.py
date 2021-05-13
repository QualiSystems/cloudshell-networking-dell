#!/usr/bin/python
# -*- coding: utf-8 -*-
from collections import OrderedDict

from cloudshell.cli.service.command_mode import CommandMode


class DefaultCommandMode(CommandMode):
    PROMPT = r'^.+>\s*$'
    ENTER_COMMAND = ''
    EXIT_COMMAND = 'exit'

    def __init__(self, resource_config):
        self.resource_config = resource_config
        CommandMode.__init__(
            self,
            self.PROMPT,
            self.ENTER_COMMAND,
            self.EXIT_COMMAND,
            use_exact_prompt=True,
        )


class EnableCommandMode(CommandMode):
    PROMPT = r'^.+#\s*$'
    ENTER_COMMAND = 'enable'
    EXIT_COMMAND = 'exit'

    def __init__(self, resource_config):
        self.resource_config = resource_config
        CommandMode.__init__(
            self,
            self.PROMPT,
            self.ENTER_COMMAND,
            self.EXIT_COMMAND,
            enter_action_map=self.enter_action_map(),
            use_exact_prompt=True,
        )

    def enter_action_map(self):
        return OrderedDict(
            [
                (
                    r"[Pp]assword",
                    lambda session, logger: session.send_line(
                        self.resource_config.enable_password
                        or self.resource_config.password,
                        logger,
                    ),
                )
            ]
        )

    def enter_actions(self, cli_service):
        cli_service.send_command("terminal length 0")


class ConfigCommandMode(CommandMode):
    PROMPT = r'^.*\(conf.*\)#\s*$'
    ENTER_COMMAND = 'configure terminal'
    EXIT_COMMAND = "exit"

    def __init__(self, resource_config):
        self.resource_config = resource_config
        CommandMode.__init__(
            self,
            self.PROMPT,
            self.ENTER_COMMAND,
            self.EXIT_COMMAND,
            use_exact_prompt=True,
        )


CommandMode.RELATIONS_DICT = {
    DefaultCommandMode: {
        EnableCommandMode: {
            ConfigCommandMode: {}
        }
    }
}


# Detached command modes

class InterfaceConfigCommandMode(CommandMode):
    PROMPT = '^.*\(conf-if-.+\)#\s*$'
    ENTER_COMMAND_TEMPLATE = 'interface {}'
    EXIT_COMMAND = 'exit'

    def __init__(self, interface_name):
        super(InterfaceConfigCommandMode, self).__init__(self.PROMPT, enter_command=self.ENTER_COMMAND_TEMPLATE.format(
            interface_name))


class VlanConfigCommandMode(InterfaceConfigCommandMode):
    ENTER_COMMAND_TEMPLATE = 'interface vlan {}'

    def __init__(self, vlan_id):
        CommandMode.__init__(self, self.PROMPT,
                             enter_command=self.ENTER_COMMAND_TEMPLATE.format(vlan_id))


class PCConfigCommandMode(InterfaceConfigCommandMode):
    ENTER_COMMAND_TEMPLATE = 'interface port-channel {}'

    def __init__(self, port_channel_id):
        CommandMode.__init__(self, self.PROMPT,
                             enter_command=self.ENTER_COMMAND_TEMPLATE.format(port_channel_id))
