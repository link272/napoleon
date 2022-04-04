import base64

from Crypto import Random
from Crypto.Cipher import AES

from napoleon.core.path.property import FilePath, Path
from napoleon.core.vault.base import BaseVault
from napoleon.properties import PlaceHolder


class AESVault(BaseVault):

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
