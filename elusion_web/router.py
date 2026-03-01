import os
import threading
import uvicorn
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

try:
    from hooks.hooks import register_hook
except ImportError:
    def register_hook(name, func):
        logging.warning(f"[Elusion Web] Hook registry not available, skipping hook: {name}")

from .settings import MODULE_PORT, API_PATH_PREFIX, MODULE_ENABLED
from .api import create_api_routes
from .telegram import (
    create_telegram_router, 
    profile_menu_hook, 
    view_key_menu_hook, 
    key_creation_complete_hook, 
    zero_traffic_notification_hook
)

# Ensure API_PATH_PREFIX ends with /
if not API_PATH_PREFIX.endswith('/'):
    API_PATH_PREFIX = API_PATH_PREFIX + '/'


def _disable_remnawave_webapp_flag():
    """Disables REMNAWAVE_WEBAPP flag to prevent conflicts"""
    patched_modules = (
        "handlers.keys.key_mode.key_cluster_mode",
        "handlers.keys.key_mode.key_country_mode",
        "handlers.notifications.special_notifications",
    )

    try:
        import config

        config.REMNAWAVE_WEBAPP = False
        logging.info("[Elusion Web] REMNAWAVE_WEBAPP overridden to False")

        for module_path in patched_modules:
            try:
                module = __import__(module_path, fromlist=["REMNAWAVE_WEBAPP"])
                if hasattr(module, "REMNAWAVE_WEBAPP"):
                    setattr(module, "REMNAWAVE_WEBAPP", False)
                    logging.info(
                        "[Elusion Web] REMNAWAVE_WEBAPP disabled in %s",
                        module_path,
                    )
            except Exception as patch_error:
                logging.warning(
                    "[Elusion Web] Could not update REMNAWAVE_WEBAPP in %s: %s",
                    module_path,
                    patch_error,
                )
    except Exception as cfg_error:
        logging.error(
            "[Elusion Web] Error disabling REMNAWAVE_WEBAPP: %s",
            cfg_error,
        )


if MODULE_ENABLED:
    _disable_remnawave_webapp_flag()


def get_version():
    """Reads version from VERSION file"""
    version_file = os.path.join(os.path.dirname(__file__), "VERSION")
    try:
        with open(version_file, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "1.0.0"


# Create aiogram router
router = create_telegram_router()

# Get module path
MODULE_PATH = os.path.dirname(__file__)
STATIC_PATH = os.path.join(MODULE_PATH, "static")

# Create FastAPI app
app = FastAPI(title="Elusion VPN API Backend", version=get_version())
create_api_routes(app, MODULE_PATH)

# Не монтируем static файлы - фронтенд на GitHub Pages


def run_fastapi_server():
    """Runs FastAPI server in daemon thread"""
    try:
        uvicorn.run(app, host="0.0.0.0", port=MODULE_PORT, log_level="warning", access_log=False)
    except Exception as e:
        logging.error(f"[Elusion Web] Server error: {e}")


# Start server in daemon thread
server_thread = threading.Thread(target=run_fastapi_server, daemon=True)
server_thread.start()

# Register hooks
register_hook("profile_menu", profile_menu_hook)
register_hook("view_key_menu", view_key_menu_hook)
register_hook("key_creation_complete", key_creation_complete_hook)
register_hook("zero_traffic_notification", zero_traffic_notification_hook)

logging.info("[Elusion Web] Hooks registered and FastAPI server started")


def get_webhook_data():
    """Legacy function for webhook compatibility"""
    from .handlers import proxy_handler
    return {
        "path": "/proxy/",
        "handler": proxy_handler
    }
