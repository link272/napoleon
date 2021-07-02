from napoleon.properties import AbstractObject
from napoleon.generators.json_schema import JSONSchema
import yaml
from jinja2 import Template
from jsonmerge import Merger


class Configurable(AbstractObject):

    @classmethod
    def from_config(cls, template_filepath, config_filepath, context):
        base_template = Template(template_filepath.read_text())
        base_string = base_template.render(context)
        base = yaml.safe_load(base_string)

        head_template = Template(config_filepath.read_text())
        head_string = head_template.render(context)
        head = yaml.safe_load(head_string)

        merger = Merger(JSONSchema().generate_schema(cls))
        config = merger.merge(base, head)

        return cls.deserialize(config)
