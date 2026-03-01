# modules/elusion_web/__init__.py

__all__ = ("router",)

from .router import router
from . import models  # noqa: F401

# ВАЖНО: Обязательно импортируем hooks, чтобы зарегистрировались кнопки в меню
from . import hooks