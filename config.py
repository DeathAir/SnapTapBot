from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "SnapTapApi"
    debug: bool = True
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/snaptapbot"
    static_dir: str = "static"


    base_url: str = "http://localhost:8000"
    verify_path: str = "/verify"

    bot_token: str = ""

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }

settings = Settings()