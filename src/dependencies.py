"""
Пакет зависимостей для FastAPI приложения.

Содержит общие зависимости, используемые в роутах приложения.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session

DataBaseSession = Annotated[AsyncSession, Depends(get_async_session)]
