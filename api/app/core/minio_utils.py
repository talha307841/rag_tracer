import os
from minio import Minio
from minio.error import S3Error

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_SECURE = False

client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE
)

def ensure_bucket(bucket_name: str):
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)

def upload_file(bucket: str, object_name: str, file_path: str):
    ensure_bucket(bucket)
    client.fput_object(bucket, object_name, file_path)

def upload_data(bucket: str, object_name: str, data: bytes, content_type: str = "application/octet-stream"):
    ensure_bucket(bucket)
    client.put_object(bucket, object_name, data, length=len(data), content_type=content_type)

def download_file(bucket: str, object_name: str, file_path: str):
    client.fget_object(bucket, object_name, file_path)

def get_object(bucket: str, object_name: str):
    return client.get_object(bucket, object_name)
