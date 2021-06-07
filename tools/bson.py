import base64
import json
import zstandard


def to_bson(struct):
    return zstandard.ZstdCompressor().compress(
        base64.urlsafe_b64encode(
            json.dumps(struct, sort_keys=True).encode()
        )
    )


def from_bson(value):
    return json.loads(
        base64.urlsafe_b64decode(
            zstandard.ZstdDecompressor().decompress(
                value
            )
        ).decode()
    )

