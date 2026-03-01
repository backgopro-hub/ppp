import logging
from aiogram import Router
from aiogram.types import InlineKeyboardButton, WebAppInfo

try:
    from config import WEBHOOK_HOST
except ImportError:
    WEBHOOK_HOST = ""

from .settings import (
    MODULE_ENABLED, BUTTON_MODE,
    API_PATH_PREFIX, WEBAPP_DOMAIN, CDN_DOMAIN, FRONTEND_URL
)

# Тексты на кнопках (по умолчанию, не требуют настройки в settings.py)
CONNECT_DEVICE_WEB = "📲 Подключить VPN"
CONNECT_DEVICE_EXTRA = "Другой способ подключения"

BACKEND_DOMAIN = WEBAPP_DOMAIN if WEBAPP_DOMAIN else WEBHOOK_HOST
BUTTON_DOMAIN = CDN_DOMAIN if CDN_DOMAIN else BACKEND_DOMAIN

# Используем фронтенд URL для кнопок
BUTTON_URL = FRONTEND_URL

# Ensure API_PATH_PREFIX ends with /
if not API_PATH_PREFIX.endswith('/'):
    API_PATH_PREFIX = API_PATH_PREFIX + '/'


def create_telegram_router():
    """Creates and returns aiogram Router"""
    router = Router()
    return router


async def _get_final_link(session, key_name):
    """Gets the final subscription link for a key"""
    if not session or not key_name:
        return None

    try:
        from database import get_key_details

        key_details = await get_key_details(session, key_name)
        if not key_details:
            return None
        return key_details.get("link") or key_details.get("remnawave_link") or key_details.get("key")
    except Exception as e:
        logging.error(f"[Elusion Web] Error getting link: {e}")
        return None


async def _is_vless_key(session, key):
    """Checks if a key is a VLESS key"""
    try:
        from modules.one_subs.router import is_vless_key
        return await is_vless_key(session, key)
    except ImportError:
        try:
            link = getattr(key, 'key', None) or getattr(key, 'remnawave_link', None)
            if link and link.lower().startswith("vless://"):
                return True
        except:
            pass
    return False


def _check_one_subs_enabled():
    """Checks if one_subs module is enabled"""
    try:
        import importlib.util
        import os

        one_subs_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "modules", "one_subs", "settings.py"
        )

        if os.path.exists(one_subs_path):
            spec = importlib.util.spec_from_file_location("one_subs_settings", one_subs_path)
            if spec and spec.loader:
                one_subs_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(one_subs_module)
                return getattr(one_subs_module, 'ENABLED', False)
    except Exception as e:
        logging.debug(f"[Elusion Web] Could not check one_subs: {e}")

    return False


def _create_connect_buttons(key_name, hook_name, final_link=None):
    """Creates connection buttons based on BUTTON_MODE"""
    buttons = []

    if not MODULE_ENABLED or not key_name:
        return buttons

    try:
        if not key_name or key_name.strip() == "":
            logging.warning(f"[Elusion Web] _create_connect_buttons: key_name is empty, cannot create buttons")
            return []
        
        logging.info(f"[Elusion Web] _create_connect_buttons: creating URL with key_name='{key_name}'")
        
        removal_commands = []
        if final_link:
            removal_commands.append({"remove_url": final_link})
        removal_commands.append({"remove_prefix": "connect_device|"})

        buttons.extend(removal_commands)

        # Формируем URL с параметром key_name для вашего фронтенда
        frontend_url_with_key = f"{BUTTON_URL}?key_name={key_name}"
        logging.info(f"[Elusion Web] _create_connect_buttons: frontend_url_with_key='{frontend_url_with_key}'")

        if BUTTON_MODE == "webapp":
            webapp_button = InlineKeyboardButton(
                text=CONNECT_DEVICE_WEB,
                web_app=WebAppInfo(url=frontend_url_with_key)
            )
            buttons.append({"insert_at": 0, "button": webapp_button})

        elif BUTTON_MODE == "web":
            url_button = InlineKeyboardButton(
                text=CONNECT_DEVICE_WEB,
                url=frontend_url_with_key
            )
            buttons.append({"insert_at": 0, "button": url_button})

        elif BUTTON_MODE == "webapp_extra":
            webapp_button = InlineKeyboardButton(
                text=CONNECT_DEVICE_WEB,
                web_app=WebAppInfo(url=frontend_url_with_key)
            )
            callback_button = InlineKeyboardButton(
                text=CONNECT_DEVICE_EXTRA,
                callback_data=f"connect_device|{key_name}"
            )
            buttons.append({"insert_at": 0, "button": webapp_button})
            buttons.append({"insert_at": 1, "button": callback_button})

        elif BUTTON_MODE == "web_extra":
            url_button = InlineKeyboardButton(
                text=CONNECT_DEVICE_WEB,
                url=frontend_url_with_key
            )
            callback_button = InlineKeyboardButton(
                text=CONNECT_DEVICE_EXTRA,
                callback_data=f"connect_device|{key_name}"
            )
            buttons.append({"insert_at": 0, "button": url_button})
            buttons.append({"insert_at": 1, "button": callback_button})

    except Exception as e:
        logging.error(f"[Elusion Web] Error in {hook_name}: {e}")

    return buttons


async def profile_menu_hook(chat_id: int, admin: bool, session, **kwargs):
    """Hook for profile menu - injects connection button"""
    if not MODULE_ENABLED:
        return []

    try:
        from database import get_key_count, get_keys

        key_count = await get_key_count(session, chat_id)

        if key_count == 0:
            return []

        keys = await get_keys(session, chat_id)
        if not keys:
            return []

        one_subs_enabled = _check_one_subs_enabled()

        if not one_subs_enabled:
            return []

        # Всегда показываем первый не-VLESS ключ
        target_key = None

        for key in keys:
            is_vless = await _is_vless_key(session, key)
            if not is_vless:
                target_key = key
                break

        if target_key is None:
            target_key = keys[0]


        key_name = getattr(target_key, 'email', '') or str(target_key)
        logging.info(f"[Elusion Web] profile_menu_hook: extracted key_name='{key_name}' from target_key")
        
        if not key_name or key_name.strip() == "":
            logging.warning(f"[Elusion Web] profile_menu_hook: key_name is empty, cannot create buttons")
            return []
        
        final_link = getattr(target_key, 'key', None) or getattr(target_key, 'remnawave_link', None)
        return _create_connect_buttons(key_name, "profile_menu_hook", final_link)

    except Exception as e:
        logging.error(f"[Elusion Web] Error in profile_menu_hook: {e}")

    return []


async def view_key_menu_hook(**kwargs):
    """Hook for view key menu - ОТКЛЮЧЕН"""
    # Не добавляем кнопку при просмотре ключа
    return []


async def key_creation_complete_hook(**kwargs):
    """Hook for key creation complete"""
    if not MODULE_ENABLED:
        return []

    try:
        key_name = kwargs.get("key_name")
        session = kwargs.get("session")
        final_link = await _get_final_link(session, key_name)
        return _create_connect_buttons(key_name, "key_creation_complete_hook", final_link)
    except Exception as e:
        logging.error(f"[Elusion Web] Error in key_creation_complete_hook: {e}")
        return []


async def zero_traffic_notification_hook(**kwargs):
    """Hook for zero traffic notification"""
    if not MODULE_ENABLED:
        return []

    try:
        email = kwargs.get("email")
        session = kwargs.get("session")
        final_link = await _get_final_link(session, email)
        return _create_connect_buttons(email, "zero_traffic_notification_hook", final_link)
    except Exception as e:
        logging.error(f"[Elusion Web] Error in zero_traffic_notification_hook: {e}")
        return []


def create_elusion_web_buttons(key):
    """Creates buttons for direct integration"""
    buttons = []

    if not MODULE_ENABLED:
        return buttons

    try:
        key_name = getattr(key, 'email', '') or str(key)
        frontend_url_with_key = f"{BUTTON_URL}?key_name={key_name}"

        if BUTTON_MODE == "webapp":
            webapp_button = InlineKeyboardButton(
                text=CONNECT_DEVICE_WEB,
                web_app=WebAppInfo(url=frontend_url_with_key)
            )
            buttons.append(webapp_button)

        elif BUTTON_MODE == "web":
            url_button = InlineKeyboardButton(
                text=CONNECT_DEVICE_WEB,
                url=frontend_url_with_key
            )
            buttons.append(url_button)

        elif BUTTON_MODE == "webapp_extra":
            webapp_button = InlineKeyboardButton(
                text=CONNECT_DEVICE_WEB,
                web_app=WebAppInfo(url=frontend_url_with_key)
            )
            callback_button = InlineKeyboardButton(
                text=CONNECT_DEVICE_EXTRA,
                callback_data=f"connect_device|{key_name}"
            )
            buttons.extend([webapp_button, callback_button])

        elif BUTTON_MODE == "web_extra":
            url_button = InlineKeyboardButton(
                text=CONNECT_DEVICE_WEB,
                url=frontend_url_with_key
            )
            callback_button = InlineKeyboardButton(
                text=CONNECT_DEVICE_EXTRA,
                callback_data=f"connect_device|{key_name}"
            )
            buttons.extend([url_button, callback_button])

    except Exception as e:
        logging.error(f"[Elusion Web] Error creating buttons: {e}")

    return buttons
