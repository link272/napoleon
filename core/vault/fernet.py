from napoleon.core.abstract import AbstractVault
from napoleon.core.special.path import FilePath, Path
from napoleon.properties import PlaceHolder

from cryptography.fernet import Fernet
import base64


class FernetVault(AbstractVault):

    key_filepath: Path = FilePath()
    _cipher = PlaceHolder()

    def _build_internal(self):
        key = base64.urlsafe_b64decode(self.key_filepath.read_bytes())
        self._cipher = Fernet(key)

    def decrypt(self, data):
        return self._cipher.decrypt(data.encode()).decode()

    def encrypt(self, data):
        return self._cipher.encrypt(data.encode()).decode()
