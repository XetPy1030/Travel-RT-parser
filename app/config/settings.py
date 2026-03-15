"""
Настройки приложения
"""
from pydantic import Field
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

    # News parsing
    http_timeout_seconds: float = Field(default=20.0, description="HTTP timeout")
    http_retries: int = Field(default=2, description="Retry count for HTTP requests")
    http_user_agent: str = Field(
        default="TravelRTParser/0.1 (+https://example.local)",
        description="User-Agent for scraping requests",
    )
    news_max_pages_per_topic: int = Field(default=5, description="Max pages per topic for one run")
    tatpressa_society_url: str = Field(
        default="https://www.tatpressa.ru/news/subject/obshchestvo-1.html",
        description="Tatpressa society topic URL",
    )
    tatpressa_culture_url: str = Field(
        default="https://www.tatpressa.ru/news/subject/kultura-4.html",
        description="Tatpressa culture topic URL",
    )
    tatpressa_ecology_url: str = Field(
        default="https://www.tatpressa.ru/news/subject/ekologiya-9.html",
        description="Tatpressa ecology topic URL",
    )

    # Process loops
    parser_loop_interval_seconds: int = Field(default=900, description="Parser run interval in seconds")
    sender_loop_interval_seconds: int = Field(default=120, description="Sender run interval in seconds")

    # Django backend sync
    backend_base_url: str = Field(default="http://localhost:8000", description="Django backend base URL")
    backend_news_create_path: str = Field(default="/api/news/", description="Django create news path")
    backend_token: str = Field(default="", description="Bearer token for backend sync")
    backend_timeout_seconds: float = Field(default=20.0, description="Timeout for backend API requests")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Игнорировать неизвестные переменные из .env


# Глобальный экземпляр настроек
settings = Settings()
