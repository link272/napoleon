import base64
import gzip
import hashlib
import json
import lzma

import lz4.frame
import yaml
import zstandard


class Pipeline(object):

    def __init__(self, data):
        self._data = data

    def __str__(self):
        return str(self._data)

    def __repr__(self):
        return str(self._data)

    def __eq__(self, other):
        return isinstance(other, Pipeline) and self._data == other._data

    def __len__(self):
        return len(self._data)

    def get(self):
        return self._data

    def to_json(self):
        return Pipeline(json.dumps(self._data))

    def from_json(self):
        return Pipeline(json.loads(self._data))

    def to_yaml(self, default_flow_style=False):
        return Pipeline(yaml.dump(self._data, default_flow_style=default_flow_style))

    def from_yaml(self):
        return Pipeline(yaml.safe_load(self._data))

    def to_base64(self):
        return Pipeline(base64.urlsafe_b64encode(self._data))

    def from_base64(self):
        return Pipeline(base64.urlsafe_b64decode(self._data))

    def to_bytes(self, encoding="utf-8"):
        return Pipeline(self._data.encode(encoding))

    def from_bytes(self, encoding="utf-8"):
        return Pipeline(self._data.decode(encoding))

    def to_hash(self, algorithm="sha256"):
        h = hashlib.new(algorithm)
        h.update(self._data)
        return Pipeline(h.hexdigest())

    def to_lz4(self, preset=3):
        return Pipeline(lz4.frame.compress(self._data, compression_level=preset))

    def from_lz4(self):
        return Pipeline(lz4.frame.decompress(self._data))

    def to_lzma(self, preset=3):
        return Pipeline(lzma.compress(self._data, preset=preset))

    def from_lzma(self):
        return Pipeline(lzma.decompress(self._data))

    def to_gzip(self, preset=6):
        return Pipeline(gzip.compress(self._data, compresslevel=preset))

    def from_gzip(self):
        return Pipeline(gzip.decompress(self._data))

    def to_zstd(self, preset=3, nb_threads=0):
        return Pipeline(zstandard.ZstdCompressor(level=preset, threads=nb_threads).compress(self._data))

    def from_zstd(self):
        return Pipeline(zstandard.ZstdDecompressor().decompress(self._data))

    def to_file(self, path):
        with open(path, "wb") as f:
            f.write(self._data)
        return Pipeline(path)

    @classmethod
    def from_file(cls, path):
        with open(path, "rb") as f:
            data = f.read()
        return Pipeline(data)
