# modules/elusion_web/hooks.py
from aiogram.types import InlineKeyboardButton, WebAppInfo
from hooks.hooks import register_hook
from . import settings

# Основная функция, которая регистрирует все хуки модуля
def register_ui_hooks():
    
    # Вспомогательная функция для создания кнопки
    def _get_webapp_btn():
        return InlineKeyboardButton(
            text="🚀 Подключить VPN",  # Текст кнопки в главном меню
            web_app=WebAppInfo(url=settings.FRONTEND_URL)  # Используем FRONTEND_URL
        )

    # Хук для меню /start (главное меню)
    async def start_menu_hook(**kwargs):
        return {"button": _get_webapp_btn()}

    # Хук для профиля
    async def profile_menu_hook(**kwargs):
        # Добавляем кнопку после кнопки "balance"
        return {"after": "balance", "button": _get_webapp_btn()}

    # Регистрируем хуки в системе бота
    register_hook("start_menu", start_menu_hook)
    register_hook("profile_menu", profile_menu_hook)
    
    print("DEBUG: [elusion_web] Хуки кнопок зарегистрированы через hooks.py")

# Запускаем регистрацию сразу при импорте этого файла
register_ui_hooks()