import os
import re
import urllib.parse
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "SIH26074 Weather Downscaling"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    
    # PostgreSQL Database URL loaded from .env
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/sih26074_db"
    
    # Allowed CORS Origins
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @property
    def sync_database_url(self) -> str:
        """
        Sanitize and format DATABASE_URL for SQLAlchemy + psycopg2:
        1. Strips unsupported params like pgbouncer=true.
        2. Safely URL-encodes special characters in passwords (e.g. '@').
        """
        url = self.DATABASE_URL
        
        # Remove pgbouncer query flag if present (psycopg2 does not accept pgbouncer as a libpq parameter)
        url = url.replace("?pgbouncer=true", "").replace("&pgbouncer=true", "")
        
        # Safely parse and encode credentials if password has special characters like '@'
        match = re.match(r"^(postgresql(?:\+\w+)?://)([^:]+):(.*)@([^@:]+(?::\d+)?(?:/.*)?)$", url)
        if match:
            prefix, user, password, host_and_path = match.groups()
            unquoted_pw = urllib.parse.unquote(password)
            encoded_pw = urllib.parse.quote_plus(unquoted_pw)
            url = f"{prefix}{user}:{encoded_pw}@{host_and_path}"
            
        return url

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
