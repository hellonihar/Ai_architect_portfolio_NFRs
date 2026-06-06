from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "TrustGuard AI"
    database_url: str = "sqlite+aiosqlite:///./trustguard.db"
    cors_origins: list[str] = ["http://localhost:5173"]
    simulation_interval_seconds: int = 5
    failover_cooldown_seconds: int = 30

    model_config = {"env_prefix": "TRUSTGUARD_", "env_file": ".env"}


settings = Settings()
