"""
Основной модуль приложения мессенджера.

Содержит инициализацию FastAPI приложения и подключение всех маршрутов.
Является точкой входа для запуска сервера.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.routes.system import router as system_router
from src.routes.users import router as users_router
from src.utils.migration import run_migrations


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Контекстный менеджер для управления жизненным циклом приложения."""
    # Запуск приложения
    await run_migrations()
    yield
    # Завершение работы приложения (пока пусто)


app = FastAPI(
    title="Безымянный мессенджер",
    description="Бэкенд для мессенджера с использованием FastAPI",
    version="0.1.0",
    contact={"name": "Команда разработки"},
    license_info={"name": "MIT"},
    lifespan=lifespan,
)

app.include_router(system_router)
app.include_router(users_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
