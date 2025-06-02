from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    