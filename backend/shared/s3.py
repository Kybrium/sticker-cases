from contextlib import asynccontextmanager
from aiobotocore.session import get_session
from botocore.exceptions import ClientError
import os
import io
from typing import Union

PLUG = "plug"

S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", PLUG)
S3_SECRET_ACCESS_KEY = os.getenv("S3_SECRET_ACCESS_KEY", PLUG)
S3_ENDPOINT = os.getenv("S3_ENDPOINT", PLUG)
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", PLUG)


class S3Client:
    def __init__(
            self,
            access_key: str,
            secret_key: str,
            endpoint_url: str,
            bucket_name: str,
    ):
        self.config = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "endpoint_url": f"https://{endpoint_url}",
        }
        self.bucket_name = bucket_name
        self.session = get_session()

    @asynccontextmanager
    async def get_client(self):
        async with self.session.create_client("s3", **self.config) as client:
            yield client

    async def upload_file(
            self,
            file_data: Union[bytes, io.BytesIO],
            object_name: str,
    ):

        if isinstance(file_data, bytes):
            file_data = io.BytesIO(file_data)

        file_data.seek(0)

        try:
            async with self.get_client() as client:
                await client.put_object(
                    Bucket=self.bucket_name,
                    Key=object_name,
                    Body=file_data,
                )
            print(f"File {object_name} uploaded to {self.bucket_name}")
        except ClientError as e:
            print(f"Error uploading file: {e}")

    async def delete_file(self, object_name: str):
        try:
            async with self.get_client() as client:
                await client.delete_object(Bucket=self.bucket_name, Key=object_name)
                print(f"File {object_name} deleted from {self.bucket_name}")
        except ClientError as e:
            print(f"Error deleting file: {e}")

    async def get_file(self, object_name: str, destination_path: str):
        try:
            async with self.get_client() as client:
                response = await client.get_object(Bucket=self.bucket_name, Key=object_name)
                data = await response["Body"].read()
                with open(destination_path, "wb") as file:
                    file.write(data)
                print(f"File {object_name} downloaded to {destination_path}")
        except ClientError as e:
            print(f"Error downloading file: {e}")
