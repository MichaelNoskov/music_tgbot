from minio import Minio
from minio.error import S3Error
from config.settings import settings

minio_client: Minio

def setup_minio() -> Minio:
    global minio_client

    minio_client = Minio(
        endpoint=settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=False
    )

    return minio_client

def get_minio() -> Minio:
    global minio_client

    if minio_client is None:
        raise Exception("MinIO client is not initialized. Call setup_minio() first.")
    
    return minio_client


async def upload_file(audio_file: str):
    client = get_minio()
    
    try:
        if not client.bucket_exists(settings.MINIO_BUCKET):
            client.make_bucket(settings.MINIO_BUCKET)

        client.fput_object(settings.MINIO_BUCKET, audio_file, settings.MINIO_LOCAL_STORAGE)
        print(f"File {audio_file} uploaded to bucket {settings.MINIO_BUCKET}.")
    except S3Error as e:
        print(f"Error occurred: {e}")

upload_file("A3 On The Run.flac")