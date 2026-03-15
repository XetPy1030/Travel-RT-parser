Итоговое состояние сейчас такое.

## Что уже сделано

- Разделение на 3 процесса:
  - `main.py` — автопарсер (цикл + `--once`)
  - `server.py` — FastAPI-сервер модерации
  - `sender.py` — отправитель одобренных сущностей в backend

- Новый слой парсеров:
  - `app/parsers/` с контрактами, HTTP-клиентом и Tatpressa list/detail парсерами.
  - Темы новостей: Экология / Культура / Общество.

- Оркестрация ingestion:
  - `app/services/ingestion_orchestrator.py` запускает news и имеет stubs для places/routes.

- Модель и курсоры:
  - `app/models/news.py` расширена полями темы и тех.метаданных.
  - Добавлена миграция `app/migrations/0002_auto_20260315_1755.py`.
  - Исправлен timezone warning (`aware UTC` в `last_parsed_at`).

- Серверные эндпоинты модерации:
  - `GET /health`
  - `GET /moderation/pending/news`
  - `GET /moderation/news/{id}`
  - `POST /moderation/news/{id}/approve`
  - `POST /moderation/news/{id}/reject`

- Отправитель:
  - `app/services/backend_sync_service.py` отправляет только `approved` и `not sent`.
  - Маппинг на Django News: `title`, `description`, `content`, `created_by=None`, `image_url` (временный формат).
  - Есть задел под `update/delete` (контракты, пока `NotImplemented`).

- Безопасность:
  - mTLS полностью убран.
  - Сейчас используется Bearer token (`BACKEND_TOKEN`).

- Зависимости:
  - Добавлены `fastapi`, `uvicorn`, `beautifulsoup4`.
  - Обновлён `poetry.lock`.

## Что еще не реализовано (остается)

- Реальные парсеры для `places/routes` (пока только stubs).
- Реальная auth/roles для moderation API (сейчас каркас без полноценной защиты).
- Реальное выполнение `update/delete` синхронизации в sender.
- Финализация формата загрузки изображения в Django (сейчас `image_url` как временная стратегия).

Может логирование настроить
