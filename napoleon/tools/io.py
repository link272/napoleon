import subprocess
from pathlib import Path

import yaml


def bash(command):
    output = subprocess.run(command, capture_output=True, encoding="utf-8", shell=True)
    if output.returncode != 0:
        res = output.stderr.splitlines()
    else:
        res = output.stdout.splitlines()
    return res


def load_yml(filepath):
    path = Path(filepath) if isinstance(filepath, str) else filepath
    return yaml.safe_load(path.read_text())


def save_yml(filepath, struct):
    path = Path(filepath) if isinstance(filepath, str) else filepath
    path.write_text(yaml.dump(struct, default_flow_style=False))
