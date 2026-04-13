from functools import lru_cache
from typing import Optional

from pydantic.v1 import BaseSettings, Field


class Settings(BaseSettings):
    groq_api_key: Optional[str] = Field(default=None, env="GROQ_API_KEY")
    model_name: str = Field(default="llama-3.1-8b-instant", env="MODEL_NAME")
    temperature: float = Field(default=0.7, env="TEMPERATURE")
    evaluator_temperature: float = Field(default=0.2, env="EVALUATOR_TEMPERATURE")
    max_questions: int = Field(default=5, env="MAX_QUESTIONS")
    default_position: str = Field(default="Python Developer", env="DEFAULT_POSITION")
    default_level: str = Field(default="mid", env="DEFAULT_LEVEL")
    default_interview_type: str = Field(default="technical", env="DEFAULT_INTERVIEW_TYPE")
    default_focus_area: str = Field(
        default="Python fundamentals and problem solving",
        env="DEFAULT_FOCUS_AREA"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
