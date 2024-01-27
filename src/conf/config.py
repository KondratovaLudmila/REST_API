from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


class RedisSettings(BaseSettings):
    host: str = 'localhost'
    port: int = 6379

    model_config = SettingsConfigDict(env_prefix='redis_')


class MailSettings(BaseSettings):
    username: str
    password: str
    mail_from: str
    port: int
    server: str

    model_config = SettingsConfigDict(env_prefix='mail_')


class CloudinarySettings(BaseSettings):
    cloud_name: str
    api_key: str
    api_secret: str
    folder: str

    model_config = SettingsConfigDict(env_prefix='cloudinary_')


class Settings(BaseSettings):
    sqlalchemy_database_url: str
    secret_key: str
    algorithm: str
    
    mail: MailSettings

    redis: RedisSettings

    cloudinary: CloudinarySettings


settings = Settings(mail=MailSettings(), redis=RedisSettings(), cloudinary=CloudinarySettings())