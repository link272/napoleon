from napoleon.properties import String, AbstractObject, Boolean, Integer, PlaceHolder, Map, JSON
from napoleon.core.special.path import FilePath, Path
from napoleon.core.special.secret import Secret
from napoleon.tools.singleton import Nothing

import base64
import jwt
import hashlib
import json
import lz4.frame
import lzma
import gzip
import yaml
import zlib
from jinja2 import Template as JinjaTemplate
import zstandard
import snappy


class Transformer(AbstractObject):

    def transform(self, data):
        raise NotImplementedError


class JsonEncoder(Transformer):

    sort_keys = Boolean()

    def transform(self, data):  # struct -> string
        return json.dumps(data, sort_keys=self.sort_keys)


class JsonDecoder(Transformer):

    def transform(self, data): # string -> struct
        return json.loads(data)


class YamlEncoder(Transformer):

    default_flow_style = Boolean()

    def transform(self, data):  # struct -> string
        return yaml.dump(data, default_flow_style=self.default_flow_style)


class YamlDecoder(Transformer):

    def transform(self, data): # string -> struct
        return yaml.safe_load(data)


class B64Encoder(Transformer):

    def transform(self, data): # byte -> bytes
        return base64.urlsafe_b64encode(data)


class B64Decoder(Transformer):

    def transform(self, data): # byte -> bytes
        return base64.urlsafe_b64decode(data)


class BytesEncoder(Transformer):

    encoding = String("utf-8")

    def transform(self, string): # string -> bytes
        return string.encode(self.encoding)


class BytesDecoder(Transformer):

    encoding = String("utf-8")

    def transform(self, _bytes): # byte -> string
        return _bytes.decode(self.encoding)


class HashEncoder(Transformer):

    algorithm: str = String("sha256", enum=["sha1", "sha224", "sha256", "sha384", "sha512", "blake2b", "blake2s", "md5"])

    def transform(self, string):
        h = hashlib.new(self.algorithm)
        h.update(string.encode())
        return h.hexdigest()


class MapEncoder(Transformer):

    mapping: dict = Map(String())
    template = JSON(default=dict)

    def transform(self, base):
        head = self.template.copy()
        for map1, map2 in self.mapping.items():
            paths = map1.split(".")
            level = base
            for path in paths:
                level = level.get(path, None)
                if level is None:
                    break
            value = level
            if value is not None:
                paths = map2.split(".")
                level = head
                for path in paths[:-1]:
                    level = level.setdefault(path, {})
                level[paths[-1]] = value
        return head


class SymmetricTokenEncoder(Transformer):

    secret = Secret()
    algorithm = String('HS256')

    def transform(self, data):
        return jwt.encode(data, self.secret, algorithm=self.algorithm)


class SymmetricTokenDecoder(Transformer):

    secret = Secret()
    algorithm = String('HS256')
    verify = Boolean(default=True)

    def transform(self, data):
        return jwt.decode(data, self.secret, algorithm=self.algorithm, verify=self.verify)


class AsymmetricTokenEncoder(Transformer):

    private_key: Path = FilePath()
    algorithm = String('RS256')

    def transform(self, data):
        return jwt.encode(data, self.private_key.read_bytes(), algorithm=self.algorithm)


class AsymmetricTokenDecoder(Transformer):

    public_key: Path = FilePath()
    algorithm = String('RS256')
    verify = Boolean(default=True)

    def transform(self, data):
        return jwt.decode(data, self.public_key.read_bytes(), algorithm=self.algorithm, verify=self.verify)


class Compressor(Transformer):

    def transform(self, data):
        raise NotImplementedError

    def begin(self):
        raise NotImplementedError

    def stream(self, data):
        raise NotImplementedError

    def flush(self):
        raise NotImplementedError


class LZ4Encoder(Compressor):

    preset = Integer(3, minimum=0, maximum=16)
    _context = PlaceHolder()

    def transform(self, data):  # byte -> bytes
        return lz4.frame.compress(data, compression_level=self.preset)

    def begin(self):
        self._context = lz4.frame.create_compression_context()
        return lz4.frame.compress_begin(self._context, compression_level=self.preset)

    def stream(self, data):
        return lz4.frame.compress_chunk(self._context, data)

    def flush(self):
        data = lz4.frame.compress_flush(self._context)
        self._context = Nothing
        return data


class LZ4Decoder(Compressor):

    _context = PlaceHolder()

    def transform(self, data): # byte -> bytes
        return lz4.frame.decompress(data)

    def begin(self):
        self._context = lz4.frame.create_decompression_context()
        return b""

    def stream(self, data):
        return lz4.frame.decompress_chunk(self._context, data)

    def flush(self):
        self._context = Nothing
        return b""


class LZMAEncoder(Compressor):

    preset: int = Integer(3, minimum=1, maximum=9)
    _engine = PlaceHolder()

    def transform(self, data): # byte -> bytes
        return lzma.compress(data, preset=self.preset)

    def begin(self):
        self._engine = lzma.LZMACompressor(preset=self.preset)
        return b""

    def stream(self, data):
        return self._engine.compress(data)

    def flush(self):
        data = self._engine.flush()
        self._engine = Nothing
        return data


class LZMADecoder(Compressor):

    _engine = PlaceHolder()

    def transform(self, data): # byte -> bytes
        return lzma.decompress(data)

    def begin(self):
        self._engine = lzma.LZMADecompressor()
        return b""

    def stream(self, data):
        return self._engine.decompress(data)

    def flush(self):
        self._engine = Nothing
        return b""


class GZIPEncoder(Compressor):

    preset = Integer(6, minimum=1, maximum=9)
    _engine = PlaceHolder()

    def transform(self, data): # byte -> bytes
        return gzip.compress(data, compresslevel=self.preset)

    def begin(self):
        self._engine = zlib.compressobj(wbits=zlib.MAX_WBITS | 16)
        return b""

    def stream(self, data):
        return self._engine.compress(data)

    def flush(self):
        data = self._engine.flush()
        self._engine = Nothing
        return data


class GZIPDecoder(Compressor):

    _engine = PlaceHolder()

    def transform(self, data): # byte -> bytes
        return gzip.decompress(data)

    def begin(self):
        self._engine = zlib.decompressobj(wbits=zlib.MAX_WBITS | 16)
        return b""

    def stream(self, data):
        return self._engine.decompress(data)

    def flush(self):
        data = self._engine.flush()
        self._engine = Nothing
        return data


class SnappyEncoder(Compressor):

    preset = Integer(6, minimum=1, maximum=9)
    _engine = PlaceHolder()

    def transform(self, data): # byte -> bytes
        return snappy.compress(data)

    def begin(self):
        self._engine = snappy.StreamCompressor()
        return b""

    def stream(self, data):
        return self._engine.compress(data)

    def flush(self):
        data = self._engine.flush()
        self._engine = Nothing
        return data


class SnappyDecoder(Compressor):

    _engine = PlaceHolder()

    def transform(self, data):  # bytes -> bytes
        return snappy.decompress(data)

    def begin(self):
        self._engine = snappy.StreamDecompressor()
        return b""

    def stream(self, data):
        return self._engine.decompress(data)

    def flush(self):
        data = self._engine.flush()
        self._engine = Nothing
        return data


class ZSTDEncoder(Compressor):

    preset: int = Integer(3, minimum=1, maximum=22)
    nb_threads: int = Integer(0)
    _engine = PlaceHolder()

    def transform(self, data):  # bytes -> bytes
        return zstandard.ZstdCompressor(level=self.preset, threads=self.nb_threads).compress(data)

    def begin(self):
        self._engine = zstandard.ZstdCompressor(level=self.preset).compressobj()
        return b""

    def stream(self, data):
        return self._engine.compress(data)

    def flush(self):
        data = self._engine.flush(zstandard.COMPRESSOBJ_FLUSH_FINISH)
        self._engine = Nothing
        return data


class ZSTDDecoder(Compressor):

    _engine = PlaceHolder()

    def transform(self, data):  # bytes -> bytes
        return zstandard.ZstdDecompressor().decompress(data)

    def begin(self):
        self._engine = zstandard.ZstdDecompressor().decompressobj()
        return b""

    def stream(self, data):
        return self._engine.decompress(data)

    def flush(self):
        data = self._engine.flush()
        self._engine = Nothing
        return data


class NaiveCompressor(Compressor):

    def transform(self, data):
        return data

    def begin(self): # noqa
        return b""

    def stream(self, data): # noqa
        return data

    def flush(self): # noqa
        return b""


class Template(Transformer):

    template: Path = FilePath()

    def transform(self, content):
        engine = JinjaTemplate(self.template.read_text())
        return engine.render(content)


class Content(object):

    def __init__(self, data):
        self._data = data

    def __str__(self):
        return str(self._data)

    def __repr__(self):
        return str(self._data)

    def __eq__(self, other):
        return isinstance(other, Content) and self._data == other._data

    def __len__(self):
        return len(self._data)

    def get(self):
        return self._data

    def to_json(self):
        return Content(json.dumps(self._data))

    def from_json(self):
        return Content(json.loads(self._data))

    def to_yaml(self, default_flow_style=False):
        return Content(yaml.dump(self._data, default_flow_style=default_flow_style))

    def from_yaml(self):
        return Content(yaml.safe_load(self._data))

    def to_base64(self):
        return Content(base64.urlsafe_b64encode(self._data))

    def from_base64(self):
        return Content(base64.urlsafe_b64decode(self._data))

    def to_bytes(self, encoding="utf-8"):
        return Content(self._data.encode(encoding))

    def from_bytes(self, encoding="utf-8"):
        return Content(self._data.decode(encoding))

    def to_hash(self, algorithm="sha256"):
        h = hashlib.new(algorithm)
        h.update(self._data)
        return Content(h.hexdigest())

    def to_symmetric_token(self, secret, algorithm='HS256'):
        return Content(jwt.encode(self._data, secret, algorithm=algorithm))

    def from_symmetric_token(self, secret, algorithm='HS256', verify=True):
        return Content(jwt.decode(self._data, secret, algorithm=algorithm, verify=verify))

    def to_asymmetric_token(self, private_key_path, algorithm='RS256'):
        return Content(jwt.encode(self._data, private_key_path.read_bytes(), algorithm=algorithm))

    def from_asymmetric_token(self, public_key_path, algorithm='RS256', verify=True):
        return Content(jwt.decode(self._data, public_key_path.read_bytes(), algorithm=algorithm, verify=verify))

    def to_lz4(self, preset=3):
        return Content(lz4.frame.compress(self._data, compression_level=preset))

    def from_lz4(self):
        return Content(lz4.frame.decompress(self._data))

    def to_lzma(self, preset=3):
        return Content(lzma.compress(self._data, preset=preset))

    def from_lzma(self):
        return Content(lzma.decompress(self._data))

    def to_gzip(self, preset=6):
        return Content(gzip.compress(self._data, compresslevel=preset))

    def from_gzip(self):
        return Content(gzip.decompress(self._data))

    def to_snappy(self):
        return Content(snappy.compress(self._data))

    def from_snappy(self):
        return Content(snappy.decompress(self._data))

    def to_zstd(self, preset=3, nb_threads=0):
        return Content(zstandard.ZstdCompressor(level=preset, threads=nb_threads).compress(self._data))

    def from_zstd(self):
        return Content(zstandard.ZstdDecompressor().decompress(self._data))

    def to_file(self, path):
        with open(path, "wb") as f:
            f.write(self._data)
        return Content(path)

    @classmethod
    def from_file(cls, path):
        with open(path, "rb") as f:
            data = f.read()
        return Content(data)
