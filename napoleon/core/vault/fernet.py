from cryptography.fernet import Fernet

from napoleon.core.path.property import FilePath, Path
from napoleon.core.vault.base import BaseVault
from napoleon.properties import PlaceHolder


class FernetVault(BaseVault):

    key: Path = FilePath()
    _cipher = PlaceHolder()

    def _build_internal(self):
        key = self.key.read_bytes()
        self._cipher = Fernet(key)

    def decrypt(self, data):
        return self._cipher.decrypt(data.encode()).decode()

    def encrypt(self, data):
        return self._cipher.encrypt(data.encode()).decode()
