from pydantic import BaseSettings, Field, BaseConfig


class Settings(BaseSettings):
    class Config(BaseConfig):
        env_file = ".env"
        env_file_encoding = "utf-8"

    DATABASE_URL: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_DEFAULT_REGION: str
    AWS_LAMBDA_ROLE: str
    AWS_BUCKET_NAME: str
    GITHUB_TOKEN: str
    OPENAI_API_KEY: str


env = Settings()
