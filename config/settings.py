from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str
    BOT_WEBHOOK_URL: str 
 
    MINIO_PORT: int 
    MINIO_API_PORT: int
    MINIO_ENDPOINT: str 
    MINIO_ROOT_USER: str 
    MINIO_ROOT_PASSWORD: str 
    MINIO_BUCKET: str 
    MINIO_LOCAL_STORAGE: str 
    MINIO_ACCESS_KEY: str 
    MINIO_SECRET_KEY: str 

    class Config:
        env_file = ".env"


settings = Settings()