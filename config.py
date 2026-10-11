from pathlib import Path

from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):

    app_name: str = "SnapTapApi"
    debug: bool = False
    static_dir: str = "static"
    base_url: str = "http://localhost:8000"
    verify_path: str = "/verify"

    database_url: str
    superadmin_id: int
    api_key: str
    bot_token: str

    model_config = {
        "env_file": str(BASE_DIR / ".env"),
        "env_file_encoding": "utf-8",
    }


settings = Settings()