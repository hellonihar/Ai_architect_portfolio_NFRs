from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "HR Bias Audit"
    debug: bool = False
    bias_threshold: float = 0.8


settings = Settings()
