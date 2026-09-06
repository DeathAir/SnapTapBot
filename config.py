


class Settings:
    app_name: str = "SnapTapApi"
    debug: bool = True
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/snaptapbot"
    static_dir: str = "static"


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()