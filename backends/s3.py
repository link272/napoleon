import boto3

import pendulum
from napoleon.core.network.http import HTTPClient
from napoleon.core.network.service import Service
from napoleon.core.utils.encoders import Content
from napoleon.properties import DateTime, Integer, String, AbstractObject, PlaceHolder


class S3Client(HTTPClient):

    _session = PlaceHolder()

    def _build_internal(self):
        super()._build_internal() # noqa
        self._session = boto3.Session(aws_access_key_id=self.user, aws_secret_access_key=self.password)

    @property
    def boto_resource(self):
        return self._session.resource(
            's3',
            endpoint_url=self.scheme + "://" + self.host,
            verify=self.verify)

    @property
    def boto_client(self):
        return self.boto_resource.meta.client


class S3Object(AbstractObject):

    key = String()
    last_modified = DateTime()
    size = Integer()
    bucket = String()
    client_name = String()

    @classmethod
    def from_item(cls, item, bucket, client_name):
        key = item["Key"]
        last_modified = pendulum.instance(item["LastModified"])
        size = item["Size"]
        return cls(key=key, last_modified=last_modified, size=size, bucket=bucket, client_name=client_name)

    @classmethod
    def from_object(cls, key, bucket, obj, client_name):
        last_modified = pendulum.instance(obj["LastModified"])
        size = obj["ContentLength"]
        return cls(key=key, bucket=bucket, size=size, last_modified=last_modified, client_name=client_name)

    def __str__(self):
        return self.key

    def __repr__(self):
        return self.key

    def content(self):
        return Content(S3Interface(client=self.client_name).stream(self.bucket, self.key).read())


class S3Interface(Service):

    def _check_internal(self):
        super()._check_internal()  # noqa
        assert isinstance(self.client, S3Client)

    def list(self, bucket, prefix=""):
        return [S3Object.from_item(obj, bucket, self.client.name) for obj in
                self.client.boto_client.list_objects_v2(Bucket=bucket, Prefix=prefix).get("Contents", [])]

    def head(self, bucket, key):
        return S3Object.from_object(key, bucket, self.client.boto_client.head_object(Bucket=bucket, Key=key), self.client.name)

    def upload(self, path, bucket, key):
        self.client.boto_client.upload_file(path, bucket, key)

    def download(self, bucket, key, path):
        self.client.boto_client.download_file(bucket, key, path)

    def delete(self, bucket, key):
        self.client.boto_client.delete_object(Bucket=bucket, Key=key)

    def clone(self, bucket1, key1, bucket2, key2):
        self.client.boto_client.copy({"Bucket": bucket1, "Key": key1}, bucket2, key2)

    def stream(self, bucket, key):
        return self.client.boto_resource.Object(bucket, key).get()["Body"]
