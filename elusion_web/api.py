import asyncio
import logging
import os
import time
from datetime import datetime, timezone
from fastapi import HTTPException, Query, Request
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import re


DEFAULT_API_PATH_PREFIX = "/elusion/api"


def normalize_path_prefix(prefix: str) -> str:
    """
    Normalizes path prefix to ensure consistent format.

    Args:
        prefix: Raw path prefix from configuration

    Returns:
        Normalized prefix with leading slash and trailing slash

    Raises:
        ValueError: If prefix contains invalid characters
    """
    # Handle empty or whitespace-only input
    if not prefix or not prefix.strip():
        logging.warning(f"[Elusion Web] PATH_PREFIX is empty, using default: {DEFAULT_API_PATH_PREFIX}")
        return f"{DEFAULT_API_PATH_PREFIX}/"

    # Strip whitespace
    prefix = prefix.strip()

    # Validate characters (alphanumeric, hyphens, underscores, forward slashes only)
    if not re.match(r'^[a-zA-Z0-9/_-]+$', prefix):
        raise ValueError(
            f"Invalid PATH_PREFIX '{prefix}': contains invalid characters. "
            "Allowed: alphanumeric, hyphens, underscores, forward slashes"
        )

    # Ensure leading slash
    if not prefix.startswith('/'):
        prefix = '/' + prefix

    # Ensure trailing slash
    if not prefix.endswith('/'):
        prefix = prefix + '/'

    return prefix

# Import configuration from main bot config
try:
    from config import (
        SUPPORT_CHAT_URL, USERNAME_BOT, WEBHOOK_HOST, 
        PROJECT_NAME, DATABASE_URL, HAPP_CRYPTOLINK, SUPERNODE
    )
except ImportError:
    # Fallback values for testing
    SUPPORT_CHAT_URL = ""
    USERNAME_BOT = ""
    WEBHOOK_HOST = ""
    PROJECT_NAME = "Elusion VPN"
    DATABASE_URL = ""
    HAPP_CRYPTOLINK = False
    SUPERNODE = False

try:
    from database.models import Key, Server, Base
except ImportError:
    Key = None
    Server = None
    Base = None

from .settings import (
    APPS_ENABLED, DEEPLINKS, APP_LINKS, BUTTONS_ENABLED, CURRENT_THEME, 
    LANGUAGE_MODE, FALLBACK_LANGUAGE, API_PATH_PREFIX, LEGACY_PATHS_ENABLED, FRONTEND_URL, BOT_URL, APP_NAME,
    RATE_LIMIT_ENABLED, RATE_LIMIT_REQUESTS, RATE_LIMIT_PERIOD, RATE_LIMIT_BLOCK_TIME, 
    HAPTIC_ENABLED, VLESS_SELECTOR_ENABLED,
    WEBAPP_DOMAIN, CDN_DOMAIN, GRADIENT_THEME_COLORS, ONBOARDING_ENABLED, ONBOARDING_STEPS
)

# Determine backend and button domains
BACKEND_DOMAIN = WEBAPP_DOMAIN if WEBAPP_DOMAIN else WEBHOOK_HOST
BUTTON_DOMAIN = CDN_DOMAIN if CDN_DOMAIN else BACKEND_DOMAIN
USE_CDN = bool(CDN_DOMAIN)

# Normalize the API path prefix at module load time
normalized_prefix = normalize_path_prefix(API_PATH_PREFIX)

# Rate limiting storage
rate_limit_storage = {
    "requests": {},
    "blocked": {}
}

# Database session maker singleton
_module_engine = None
_module_session_maker = None


def get_module_session_maker():
    """Returns async SQLAlchemy session maker (singleton pattern)"""
    global _module_engine, _module_session_maker
    if _module_session_maker is None:
        _module_engine = create_async_engine(
            DATABASE_URL,
            echo=False,
            future=True,
            pool_size=5,
            max_overflow=10,
            pool_timeout=15
        )
        _module_session_maker = async_sessionmaker(
            bind=_module_engine,
            expire_on_commit=False,
            class_=AsyncSession
        )
    return _module_session_maker


def get_all_texts(language="ru"):
    """Merges static and dynamic text dictionaries for the given language"""
    from .texts import STATIC_TEXTS, DINAMIC_TEXTS
    
    texts = {}
    texts.update(STATIC_TEXTS.get(language, STATIC_TEXTS.get("ru", {})))
    texts.update(DINAMIC_TEXTS.get(language, DINAMIC_TEXTS.get("ru", {})))
    return texts


def get_client_ip(request: Request) -> str:
    """Extracts client IP from request headers"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    return request.client.host if request.client else "unknown"


def check_rate_limit(ip: str) -> bool:
    """Validates request rate against limits"""
    if not RATE_LIMIT_ENABLED:
        return True

    current_time = time.time()

    # Check if IP is blocked
    if ip in rate_limit_storage["blocked"]:
        block_until = rate_limit_storage["blocked"][ip]
        if current_time < block_until:
            return False
        else:
            del rate_limit_storage["blocked"][ip]

    # Initialize request list for IP
    if ip not in rate_limit_storage["requests"]:
        rate_limit_storage["requests"][ip] = []

    # Clean up expired timestamps
    rate_limit_storage["requests"][ip] = [
        req_time for req_time in rate_limit_storage["requests"][ip]
        if current_time - req_time < RATE_LIMIT_PERIOD
    ]

    # Check if limit exceeded
    if len(rate_limit_storage["requests"][ip]) >= RATE_LIMIT_REQUESTS:
        rate_limit_storage["blocked"][ip] = current_time + RATE_LIMIT_BLOCK_TIME
        logging.warning(f"[Elusion Web] IP {ip} blocked for {RATE_LIMIT_BLOCK_TIME}s")
        return False

    # Add current request
    rate_limit_storage["requests"][ip].append(current_time)
    return True


def create_api_routes(app, module_path):
    """Registers all endpoints and middleware to the FastAPI app"""
    
    logging.info("[Elusion Web] Starting to register API routes...")
    logging.info(f"[Elusion Web] API_PATH_PREFIX configured: {normalized_prefix}")
    logging.info(f"[Elusion Web] Legacy paths enabled: {LEGACY_PATHS_ENABLED}")
    
    # Configure CORS - добавляем ваш GitHub Pages фронтенд
    allowed_origins = [
        BACKEND_DOMAIN,
        FRONTEND_URL,
        "https://backgopro-hub.github.io"  # Весь домен GitHub Pages
    ]
    
    if USE_CDN and CDN_DOMAIN and CDN_DOMAIN != BACKEND_DOMAIN:
        allowed_origins.append(CDN_DOMAIN)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    # Security headers middleware
    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)

        response.headers["Content-Security-Policy"] = (
            "frame-ancestors 'self' https://web.telegram.org https://telegram.org; "
            "script-src 'self' 'unsafe-inline' https://telegram.org https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://cdn.tailwindcss.com"
        )

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        return response

    # API Endpoints (только бэкенд, без HTML)
    
    # Тестовый endpoint без API_PATH_PREFIX
    @app.get("/test")
    async def test_endpoint():
        """Test endpoint"""
        return {"status": "ok", "message": "Test endpoint works!"}
    
    @app.get(f"{normalized_prefix}health")
    async def health_check():
        """Health check endpoint"""
        try:
            session_maker = get_module_session_maker()
            async with session_maker() as session:
                await session.execute(select(1))
                db_status = "ok"
        except Exception:
            db_status = "unavailable"
        return JSONResponse(content={"status": "ok", "database": db_status, "module": "elusion_web"})

    @app.get(f"{normalized_prefix}settings")
    async def get_settings():
        """Returns configuration settings for frontend"""
        return JSONResponse(content={
            "project_name": PROJECT_NAME,
            "app_name": APP_NAME,  # Название приложения из settings.py
            "bot_username": USERNAME_BOT,
            "support_chat": SUPPORT_CHAT_URL,
            "webhook_host": BUTTON_DOMAIN,
            "bot_url": BOT_URL,  # URL бота из settings.py
            "base_path": normalized_prefix,
            "api_path_prefix": normalized_prefix,
            "color_theme": CURRENT_THEME,
            "gradient_colors": GRADIENT_THEME_COLORS,
            "language": {
                "default_mode": LANGUAGE_MODE,
                "fallback": FALLBACK_LANGUAGE
            },
            "apps": APPS_ENABLED,
            "deeplinks": DEEPLINKS,
            "app_links": APP_LINKS,
            "buttons": BUTTONS_ENABLED,
            "happ_cryptolink": HAPP_CRYPTOLINK,
            "haptic_enabled": HAPTIC_ENABLED,
            "vless_selector_enabled": VLESS_SELECTOR_ENABLED,
            "onboarding_enabled": ONBOARDING_ENABLED,
            "onboarding_steps": ONBOARDING_STEPS
        })

    @app.get(f"{normalized_prefix}texts")
    async def get_texts(language: str = "ru"):
        """Returns UI texts for the requested language"""
        texts = get_all_texts(language)
        return JSONResponse(content={"texts": texts, "language": language})


    @app.get(f"{normalized_prefix}sub")
    async def get_sub(request: Request, key_name=Query(None)):
        """Returns subscription details for a given key"""
        client_ip = get_client_ip(request)
        if not check_rate_limit(client_ip):
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again in 5 minutes."
            )

        if not key_name:
            raise HTTPException(status_code=400, detail="Required key_name parameter")

        try:
            session_maker = get_module_session_maker()
            async with session_maker() as session:
                query = select(Key).where(
                    Key.email == key_name,
                    Key.is_frozen == False
                ).limit(1)

                result = await session.execute(query)
                row = result.scalar_one_or_none()

                if not row:
                    raise HTTPException(status_code=404, detail="Subscription not found")
                
                expiry_iso = datetime.fromtimestamp(row.expiry_time / 1000, timezone.utc).isoformat()
                remnawave_link = getattr(row, "remnawave_link", None)

                # Check if key is crypto link
                key_is_crypto = row.key and row.key.startswith('happ://crypt')

                if HAPP_CRYPTOLINK:
                    if key_is_crypto:
                        primary_link = row.key
                        is_crypto_link = True
                    else:
                        primary_link = row.key or remnawave_link
                        is_crypto_link = False
                else:
                    primary_link = row.key or remnawave_link
                    is_crypto_link = False

                return {
                    "key": row.key,
                    "expiry": expiry_iso,
                    "link": primary_link,
                    "email": getattr(row, "email", ""),
                    "is_crypto_link": is_crypto_link,
                    "remnawave_link": remnawave_link if HAPP_CRYPTOLINK else None,
                }

        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"[Elusion Web] Database error: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    @app.get(f"{normalized_prefix}keys/{{tg_id}}")
    async def get_user_keys(request: Request, tg_id: int):
        """Returns all keys for a given Telegram user ID"""
        client_ip = get_client_ip(request)
        if not check_rate_limit(client_ip):
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again in 5 minutes."
            )

        try:
            session_maker = get_module_session_maker()
            async with session_maker() as session:
                query = select(Key).where(
                    Key.tg_id == tg_id,
                    Key.is_frozen == False
                )

                result = await session.execute(query)
                rows = result.scalars().all()

                if not rows:
                    return []

                keys_list = []
                for row in rows:
                    expiry_iso = datetime.fromtimestamp(row.expiry_time / 1000, timezone.utc).isoformat()
                    keys_list.append({
                        "id": row.id,
                        "email": getattr(row, "email", ""),
                        "key": row.key,
                        "expiry": expiry_iso,
                        "tg_id": row.tg_id
                    })

                return keys_list

        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"[Elusion Web] Database error: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    @app.get(f"{normalized_prefix}qr")
    async def get_qr_code(request: Request, key_name: str = Query(None)):
        """Generates QR code for subscription link"""
        client_ip = get_client_ip(request)
        if not check_rate_limit(client_ip):
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again in 5 minutes."
            )

        if not key_name:
            raise HTTPException(status_code=400, detail="Required key_name parameter")

        try:
            import qrcode
            from io import BytesIO

            session_maker = get_module_session_maker()
            async with session_maker() as session:
                query = select(Key).where(
                    Key.email == key_name,
                    Key.is_frozen == False
                ).limit(1)

                result = await session.execute(query)
                row = result.scalar_one_or_none()

                if not row:
                    raise HTTPException(status_code=404, detail="Subscription not found")

                remnawave_link = getattr(row, "remnawave_link", None)
                key_is_crypto = row.key and row.key.startswith('happ://crypt')

                if HAPP_CRYPTOLINK:
                    if key_is_crypto:
                        qr_data = row.key
                    else:
                        qr_data = row.key or remnawave_link
                else:
                    qr_data = row.key or remnawave_link

                if not qr_data:
                    raise HTTPException(status_code=404, detail="No subscription link available")

                logging.info(f"[Elusion Web] Generating QR for key: {key_name}, data length: {len(qr_data)}")

                qr = qrcode.QRCode(version=1, box_size=10, border=1)
                qr.add_data(qr_data)
                qr.make(fit=True)

                img = qr.make_image(fill_color="black", back_color="white")
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                buffer.seek(0)

                return StreamingResponse(buffer, media_type="image/png")

        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"[Elusion Web] QR code generation error: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    @app.post(f"{normalized_prefix}tv")
    async def send_to_tv(request: Request):
        """Sends subscription to TV device via Happ API"""
        client_ip = get_client_ip(request)
        if not check_rate_limit(client_ip):
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again in 5 minutes."
            )

        try:
            import httpx

            data = await request.json()
            code = data.get("code")
            subscription_data = data.get("data")

            if not code or not subscription_data:
                return JSONResponse(
                    content={"success": False, "error": "Missing code or data parameter"},
                    status_code=400
                )

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"https://check.happ.su/sendtv/{code}",
                    headers={"Content-Type": "application/json"},
                    json={"data": subscription_data}
                )

                response_text = response.text

                if response.status_code == 200:
                    return JSONResponse(
                        content={
                            "success": True,
                            "message": "Subscription sent successfully",
                            "response": response_text
                        }
                    )
                else:
                    return JSONResponse(
                        content={
                            "success": False,
                            "error": f"Happ API error: {response.status_code}",
                            "response": response_text
                        },
                        status_code=response.status_code
                    )

        except Exception as e:
            logging.error(f"[Elusion Web] Error sending to Happ API: {e}")
            return JSONResponse(
                content={"success": False, "error": str(e)},
                status_code=500
            )

    # Legacy path registration (conditional)
    if LEGACY_PATHS_ENABLED:
        logging.warning("[Elusion Web] Legacy mode enabled - endpoints accessible at multiple paths")
        
        @app.get("/api/health")
        async def legacy_health_check():
            """Legacy health check endpoint"""
            return await health_check()
        
        @app.get("/api/settings")
        async def legacy_get_settings():
            """Legacy settings endpoint"""
            return await get_settings()
        
        @app.get("/api/texts")
        async def legacy_get_texts(language: str = "ru"):
            """Legacy texts endpoint"""
            return await get_texts(language)
        
        @app.get("/api/sub")
        async def legacy_get_sub(request: Request, key_name=Query(None)):
            """Legacy subscription endpoint"""
            return await get_sub(request, key_name)
        
        @app.get("/api/qr")
        async def legacy_get_qr_code(request: Request, key_name: str = Query(None)):
            """Legacy QR code endpoint"""
            return await get_qr_code(request, key_name)
        
        @app.post("/api/tv")
        async def legacy_send_to_tv(request: Request):
            """Legacy TV send endpoint"""
            return await send_to_tv(request)

    logging.info("[Elusion Web] API routes registered successfully!")
