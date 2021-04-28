from cloudshell.cli.configurator import AbstractModeConfigurator
from cloudshell.cli.service.command_mode_helper import CommandModeHelper
from cloudshell.networking.dell.cli.dnos_command_modes import DefaultCommandMode, ConfigCommandMode, EnableCommandMode


class DNOSCliConfigurator(AbstractModeConfigurator):

    def __init__(self, resource_config, logger, cli):
        """Checkpoint cli configurator.

        :param cloudshell.shell.standards.networking.resource_config import NetworkingResourceConfig resource_config:
        :param logging.Logger logger:
        :param cloudshell.cli.service.cli.CLI cli:
        """

        super(DNOSCliConfigurator, self).__init__(resource_config, logger, cli)
        self.modes = CommandModeHelper.create_command_mode(resource_config)

    @property
    def default_mode(self):
        return self.modes.get(DefaultCommandMode)

    @property
    def enable_mode(self):
        return self.modes.get(EnableCommandMode)

    @property
    def config_mode(self):
        return self.modes.get(ConfigCommandMode)

    def default_mode_service(self):
        return self.get_cli_service(self.default_mode)
