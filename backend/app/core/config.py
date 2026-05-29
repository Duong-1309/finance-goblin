from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Finance Goblin"
    debug: bool = False
    db_path: str = "data/goblin.db"
    google_sheet_id: str = ""
    google_credentials_path: str = "credentials/google-service-account.json"
    telegram_token: str = ""
    telegram_chat_id: str = ""
    gemini_api_key: str = ""
    openai_api_key: str = ""
    monthly_budget: float = 20_000_000
    device_api_key: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
