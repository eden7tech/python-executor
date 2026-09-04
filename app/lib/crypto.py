import os
import json
import base64
import hashlib

from cryptography.fernet import Fernet


class Crypto:

    _fernet = None

    @classmethod
    def _instance(cls):

        if cls._fernet is None:

            key = os.getenv("CONFIG_ENCRYPTION_KEY")

            if not key:
                raise RuntimeError(
                    "CONFIG_ENCRYPTION_KEY não definida."
                )

            digest = hashlib.sha256(
                key.encode("utf-8")
            ).digest()

            fernet_key = base64.urlsafe_b64encode(
                digest
            )

            cls._fernet = Fernet(
                fernet_key
            )

        return cls._fernet

    @classmethod
    def encrypt(cls, obj):

        dados = json.dumps(
            obj,
            ensure_ascii=False
        ).encode("utf-8")

        return cls._instance().encrypt(
            dados
        ).decode("utf-8")

    @classmethod
    def decrypt(cls, token):

        dados = cls._instance().decrypt(
            token.encode("utf-8")
        )

        return json.loads(
            dados.decode("utf-8")
        )
