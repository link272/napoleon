from napoleon.core.special.hidden import HiddenBytes
from napoleon.core.cmd import CommandLine
from napoleon.properties import MutableSingleton, AbstractObject, String
from napoleon.tools.singleton import exist, is_define

import os
from cryptography.fernet import Fernet
import hashlib
import base64
import hmac


class Vault(AbstractObject, metaclass=MutableSingleton):

    key: bytes = HiddenBytes(Fernet.generate_key)

    @classmethod
    def from_password(cls, password: str,
                      salt="3pbXWxkVxUV7K5Uq1rGqhQ==",
                      iterations=1000000,
                      algorithm="sha256"):
        key = base64.urlsafe_b64encode(hashlib.pbkdf2_hmac(algorithm,
                                                           password.encode(),
                                                           base64.urlsafe_b64decode(salt.encode()),
                                                           iterations,
                                                           dklen=32))
        return cls(key=key)

    @property
    def cipher(self):
        return Fernet(self.key)

    def decrypt(self, data):
        return self.cipher.decrypt(data.encode()).decode()

    def encrypt(self, data):
        return self.cipher.encrypt(data.encode()).decode()

    @classmethod
    def generate_salt(cls, salt_size=16):
        return base64.urlsafe_b64encode(os.urandom(salt_size)).decode()

    def is_authorized(self, key):
        return hmac.compare_digest(self.key, key)

    @classmethod
    def from_cmd(cls):
        cmd = CommandLine.from_cmd()
        if cmd.secret_key:
            vault = cls(key=base64.urlsafe_b64decode(cmd.secret_key.encode()))
        elif cmd.password:
            vault = cls.from_password(cmd.password)
        else:
            vault = Vault()
        return vault


Vault.from_cmd()


class Secret(String):

    def from_string(self, value):
        return Vault().decrypt(value)

    def to_string(self, value):
        return Vault().encrypt(value)
