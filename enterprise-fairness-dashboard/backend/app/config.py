from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://fairness_user:fairness_pass@localhost:5432/enterprise_fairness"
    app_name: str = "Enterprise Fairness & Bias Dashboard"
    debug: bool = True
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"


settings = Settings()
