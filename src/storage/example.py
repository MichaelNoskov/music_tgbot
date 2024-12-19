from minio import Minio
from minio.error import S3Error

access_key="a1BhODJ6Z3opeZbbacV5"
secret_key="DFPjat4SAuk4HV3WhyGoywnXrWM206ZdKdXL9RaG"     
bucket_name = "audio-files"                     # Название бакета
local_storage_path = "data/buckets/audiofiles/" # Локальный путь для сохранения

minio_client = Minio(
    endpoint="localhost:9000",  # Адрес MinIO
    access_key=access_key,
    secret_key=secret_key,
    secure=False                # False, если не используете SSL
)

def download_song(audiofile):
    try:
        minio_client.fget_object(bucket_name, audiofile, f"{local_storage_path}{audiofile}")
        print(f"Файл '{audiofile}' скачан как 'f{local_storage_path}{audiofile}'.")
    except S3Error as err:
        print(f"Ошибка скачивания файла: {err}")

def upload_song(audiofile):
    try:
        minio_client.fput_object(bucket_name, audiofile, audiofile)
        print(f"Файл '{audiofile}' загружен в бакет '{bucket_name}' как '{audiofile}'.")
    except S3Error as err:
        print(f"Ошибка загрузки файла: {err}")

# upload_song("A1 Speak To Me.flac")
# download_song("A1 Speak To Me.flac")