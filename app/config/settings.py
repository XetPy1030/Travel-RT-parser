"""
Настройки приложения
"""
from typing import List, Optional, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения"""
    # Database
    postgres_db: str = Field(default="postgres", description="Имя базы данных")
    postgres_user: str = Field(default="postgres", description="Имя пользователя")
    postgres_password: str = Field(default="postgres", description="Пароль")
    postgres_host: str = Field(default="localhost", description="Хост")
    postgres_port: int = Field(default=5432, description="Порт")
    
    # Redis
    # redis_url: str = Field(
    #     default="redis://localhost:6379/0",
    #     description="URL подключения к Redis"
    # )
    
    # Logging
    log_level: str = Field(default="INFO", description="Уровень логирования")
    log_file: str = Field(default="bot.log", description="Файл логов")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Игнорировать неизвестные переменные из .env


# Глобальный экземпляр настроек
settings = Settings()
