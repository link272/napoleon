from napoleon.core.cmd.base import BaseCommandLine
from napoleon.core.path.property import FilePath, Path
from napoleon.properties import Map, String


class CommandLine(BaseCommandLine):

    config_path = FilePath(Path.cwd() / Path("config/application.yml"), description="env-related config file")
    template_path = FilePath(Path.cwd() / Path("templates/application.yml"), description="base config file")
    environment = String("local")
    vars = Map(String())
