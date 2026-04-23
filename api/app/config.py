from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gemini_api_key: str = ""
    upload_dir: str = "uploads"
    max_file_size_mb: int = 50
    allowed_extensions: list[str] = [".csv", ".xlsx"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
