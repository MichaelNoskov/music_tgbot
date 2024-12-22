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

    RABBIT_HOST: str = 'localhost'
    RABBIT_PORT: int = 5672
    RABBIT_USER: str = 'guest'
    RABBIT_PASSWORD: str = 'guest'

    USER_QUEUE: str = 'user_music.{user_id}'

    @property
    def rabbit_url(self) -> str:
        return f"amqp://{self.RABBIT_USER}:{self.RABBIT_PASSWORD}@{self.RABBIT_HOST}:{self.RABBIT_PORT}/"

    class Config:
        env_file = ".env"


settings = Settings()