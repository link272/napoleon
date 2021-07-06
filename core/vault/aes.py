from napoleon.core.abstract import AbstractVault
from napoleon.core.special.path import FilePath, Path
from napoleon.properties import PlaceHolder

import base64
from Crypto.Cipher import AES
from Crypto import Random


class AESVault(AbstractVault):

    key_filepath: Path = FilePath()
    _key = PlaceHolder()

    def _build_internal(self):
        self._key = base64.urlsafe_b64decode(self.key_filepath.read_bytes())

    def decrypt(self, data):
        iv = data[:AES.block_size]
        cypher = AES.new(self._key, AES.MODE_CBC, iv)
        msg = cypher.decrypt(data.encode()[AES.block_size:])
        padding = msg[-1]
        return msg[:-padding].decode()

    def encrypt(self, data):
        msg = data.encode()
        iv = Random.new().read(AES.block_size)
        encryptor = AES.new(self._key, AES.MODE_CBC, iv)
        padding = AES.block_size - len(msg) % AES.block_size
        msg += bytes([padding]) * padding
        return iv + encryptor.encrypt(msg)
