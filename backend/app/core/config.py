from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Finance Goblin"
    debug: bool = False
    db_path: str = "data/goblin.db"
    google_sheet_id: str = ""
    google_credentials_path: str = "credentials/google-service-account.json"
    telegram_token: str = ""
    telegram_chat_id: str = ""
    openai_api_key: str = ""
    monthly_budget: float = 20_000_000
    device_api_key: str = ""
    mqtt_broker_host: str = "localhost"
    mqtt_broker_port: int = 1883
    mqtt_topic_display: str = "goblin/display"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
