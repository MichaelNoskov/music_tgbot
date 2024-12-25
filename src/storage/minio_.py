import random

from minio import Minio
from minio.error import S3Error
from config.settings import settings
from io import BytesIO


minio_client = Minio(
    endpoint=settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ROOT_USER,
    secret_key=settings.MINIO_ROOT_PASSWORD,
    secure=False
)

async def upload_music(filename, audio_bytes):
    try:
        if not minio_client.bucket_exists(settings.MINIO_BUCKET):
            minio_client.make_bucket(settings.MINIO_BUCKET)

        minio_client.put_object(
            bucket_name=settings.MINIO_BUCKET, 
            object_name=filename, 
            data=BytesIO(audio_bytes),
            length=len(audio_bytes)
        )
        print(f"File {filename} uploaded to bucket {settings.MINIO_BUCKET}.")

    except S3Error as e:
        print(f"Error occurred: {e}")
        return


async def get_music(audiofile):
    try:
        response = minio_client.get_object(settings.MINIO_BUCKET, audiofile)
        audio_data = response.read()
        
        return audio_data, None
    
    except S3Error as e:
        print(f"Error occurred: {e}")
        return

async def get_random_music():
    objects = list(minio_client.list_objects(settings.MINIO_BUCKET))
    
    if not objects:
        print("No available files.")
        return None
    
    random_music = random.choice(objects)
    
    return random_music.object_name