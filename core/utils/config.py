from napoleon.properties import AbstractObject
from napoleon.core.paths import PATHS, Path
from napoleon.tools.io import load_yml, save_yml
from napoleon.generators.json_schema import JSONSchema
import yaml
from jinja2 import Template
from jsonmerge import Merger
import os


class Configurable(AbstractObject):

    @classmethod
    def from_config(cls, name, context):
        context.update(os.environ)
        base_template = Template((PATHS.templates / Path(name + ".yml.j2")).read_text())

        base_string = base_template.render(context)

        base = yaml.safe_load(base_string)
        head_template = Template((PATHS.config / Path(name + ".yml")).read_text())

        head_string = head_template.render(context)

        head = yaml.safe_load(head_string)

        merger = Merger(JSONSchema().generate_schema(cls))
        config = merger.merge(base, head)

        return cls.deserialize(config)

    @classmethod
    def load_yaml(cls, filepath):
        return cls.deserialize(load_yml(filepath))

    def dump_yaml(self, filepath):
        save_yml(filepath, self.serialize())
