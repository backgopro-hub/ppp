# ========================================
# 🔧 ОСНОВНЫЕ НАСТРОЙКИ МОДУЛЯ
# ========================================

# Включен ли модуль?
MODULE_ENABLED = True

# URL бота (для фронтенда)
# Этот URL будет отдаваться через /api/settings
BOT_URL = "https://bot.netelusion.com"

# Название приложения (отображается на фронтенде)
APP_NAME = "Elusion VPN"

# Какие кнопки показывать в боте?
# "webapp" = WebApp кнопка (открывается внутри Telegram)
# "web" = URL кнопка (открывается во внешнем браузере)
BUTTON_MODE = "web"

# На каком порту запускать API бэкенд?
MODULE_PORT = 3004

# Домен вашего бота (бэкенд API)
# Оставьте пустым (""), чтобы использовать WEBHOOK_HOST из config
WEBAPP_DOMAIN = ""

# CDN домен (если используется)
CDN_DOMAIN = ""

# Путь для API endpoints (бэкенд)
API_PATH_PREFIX = "/elusion/api"

# Включить поддержку старых путей для обратной совместимости
LEGACY_PATHS_ENABLED = False

# URL фронтенда на GitHub Pages
FRONTEND_URL = "https://backgopro-hub.github.io/wp/lochi.html"

# ========================================
# 🔒 БЕЗОПАСНОСТЬ
# ========================================

# Включить ограничение количества запросов
RATE_LIMIT_ENABLED = True

# Максимальное количество запросов к API с одного IP
RATE_LIMIT_REQUESTS = 20

# Период времени для подсчета запросов (в секундах)
RATE_LIMIT_PERIOD = 60

# Время блокировки IP при превышении лимита (в секундах)
RATE_LIMIT_BLOCK_TIME = 60

# ========================================
# 🌍 ЯЗЫКОВЫЕ НАСТРОЙКИ
# ========================================

# Как определять язык пользователя?
# "user" = автоматически по языку Telegram
# "ru" = всегда русский
# "en" = всегда английский
LANGUAGE_MODE = "user"

# Язык по умолчанию
FALLBACK_LANGUAGE = "ru"

# ========================================
# 🎨 ВНЕШНИЙ ВИД
# ========================================

# Тема оформления
# "dark", "light", "cyberpunk", "ocean", "fox", "gradient"
CURRENT_THEME = "fox"

# Цвета для градиентной темы
GRADIENT_THEME_COLORS = {
    "start": "#AAAAAA",
    "end": "#AAAAAA"
}

# Включить тактильную обратную связь (вибрацию)?
HAPTIC_ENABLED = True

# Показывать onboarding тур при первом посещении?
ONBOARDING_ENABLED = True

# Какие шаги онбординга показывать?
ONBOARDING_STEPS = {
    "subscription": True,
    "qr_code": True,
    "platform": True,
    "app": True,
    "steps": True,
    "get_link": True,
    "share": True
}

# Показывать селектор стран для VLESS ключей?
VLESS_SELECTOR_ENABLED = False

# ========================================
# 📱 КАКИЕ ПРИЛОЖЕНИЯ ПОКАЗЫВАТЬ
# ========================================

APPS_ENABLED = {
    "ios": {"Happ": 1, "V2rayTun": 2, "Shadowrocket": 0, "Streisand": 0, "Singbox": 0, "ClashMi": 0},
    "android": {"Happ": 1, "Hiddify": 0, "V2rayTun": 2, "FlClashX": 0, "ClashMeta": 0, "Singbox": 0, "V2rayNG": 0, "Exclave": 0},
    "windows": {"Happ": 1, "Hiddify": 0, "V2rayTun": 2, "Koalaclash": 0, "FlClashX": 0, "ClashVerge": 0},
    "macos": {"Happ": 1, "Hiddify": 0, "Shadowrocket": 0, "V2rayTun": 2, "Koalaclash": 0, "ClashVerge": 0, "Singbox": 0},
    "linux": {"Hiddify": 0, "Happ": 1},
    "appletv": {"Happ": 1},
    "androidtv": {"Happ": 1}
}

# ========================================
# 🔘 КАКИЕ КНОПКИ СКАЧИВАНИЯ ПОКАЗЫВАТЬ
# ========================================

BUTTONS_ENABLED = {
    "ios": {
        "happ_1": 0, "happ_2": 2,
        "v2raytun_1": 1,
        "shadowrocket_1": 1,
        "streisand_1": 1,
        "singbox_1": 1,
        "clashmi_1": 1
    },
    "android": {
        "happ_1": 1, "happ_2": 2,
        "hiddify_1": 1,
        "v2raytun_1": 1, "v2raytun_2": 2,
        "flclashx_1": 1,
        "clashmeta_1": 1,
        "singbox_1": 1, "singbox_2": 2,
        "v2rayng_1": 1,
        "exclave_1": 1
    },
    "windows": {
        "happ_1": 1,
        "hiddify_1": 1,
        "v2raytun_1": 1,
        "koalaclash_1": 1,
        "flclashx_1": 1,
        "clashverge_1": 1
    },
    "macos": {
        "happ_1": 0, "happ_2": 2, "happ_3": 3,
        "hiddify_1": 1,
        "v2raytun_1": 1,
        "shadowrocket_1": 1,
        "koalaclash_1": 1,
        "singbox_1": 1,
        "clashverge_1": 1, "clashverge_2": 2
    },
    "linux": {
        "hiddify_1": 1,
        "happ_1": 1
    },
    "appletv": {"happ_1": 1},
    "androidtv": {"happ_1": 1}
}

# ========================================
# 📥 ССЫЛКИ ДЛЯ СКАЧИВАНИЯ ПРИЛОЖЕНИЙ
# ========================================

APP_LINKS = {
    "ios": {
        "happ_1": "https://apps.apple.com/ru/app/happ-proxy-utility-plus/id6746188973",
        "happ_2": "https://apps.apple.com/us/app/happ-proxy-utility/id6504287215",
        "v2raytun_1": "https://apps.apple.com/ru/app/v2raytun/id6476628951",
        "shadowrocket_1": "https://apps.apple.com/ru/app/shadowrocket/id932747118",
        "streisand_1": "https://apps.apple.com/us/app/streisand/id6450534064",
        "singbox_1": "https://apps.apple.com/app/sing-box-vt/id6673731168",
        "clashmi_1": "https://apps.apple.com/ru/app/clash-mi/id6744321968"
    },
    "android": {
        "happ_1": "https://play.google.com/store/apps/details?id=com.happproxy",
        "happ_2": "https://github.com/Happ-proxy/happ-android/releases/latest/download/Happ_beta.apk",
        "hiddify_1": "https://github.com/hiddify/hiddify-next/releases/download/v2.5.7/Hiddify-Android-universal.apk",
        "v2raytun_1": "https://play.google.com/store/apps/details?id=com.v2raytun.android",
        "v2raytun_2": "https://github.com/ADDVPN/v2raytun/releases/download/v1.3/v2RayTun_universal_3_12_46.apk",
        "flclashx_1": "https://github.com/pluralplay/FlClashX/releases/download/v0.2.0/FlClashX-0.2.0-android-arm64-v8a.apk",
        "clashmeta_1": "https://github.com/MetaCubeX/ClashMetaForAndroid/releases/download/v2.11.15/cmfa-2.11.15-meta-universal-release.apk",
        "singbox_1": "https://play.google.com/store/apps/details?id=io.nekohasekai.sfa",
        "singbox_2": "https://github.com/SagerNet/sing-box/releases/download/v1.11.10/SFA-1.11.10-universal.apk",
        "v2rayng_1": "https://github.com/2dust/v2rayNG/releases/download/1.10.1/v2rayNG_1.10.1_universal.apk",
        "exclave_1": "https://github.com/dyhkwong/Exclave/releases/download/0.14.5/Exclave-0.14.5-arm64-v8a.apk"
    },
    "windows": {
        "happ_1": "https://github.com/Happ-proxy/happ-desktop/releases/latest/download/setup-Happ.x64.exe",
        "hiddify_1": "https://github.com/hiddify/hiddify-next/releases/download/v2.5.7/Hiddify-Windows-Setup-x64.exe",
        "v2raytun_1": "https://storage.v2raytun.com/v2RayTun_Setup.exe",
        "koalaclash_1": "https://github.com/coolcoala/clash-verge-rev-lite/releases/latest/download/Koala.Clash_x64-setup.exe",
        "flclashx_1": "https://github.com/pluralplay/FlClashX/releases/download/v0.2.0/FlClashX-0.2.0-windows-amd64-setup.exe",
        "clashverge_1": "https://github.com/clash-verge-rev/clash-verge-rev/releases/download/v2.2.2/Clash.Verge_2.2.2_x64-setup.exe"
    },
    "macos": {
        "happ_1": "https://apps.apple.com/ru/app/happ-proxy-utility-plus/id6746188973",
        "happ_2": "https://apps.apple.com/us/app/happ-proxy-utility/id6504287215",
        "happ_3": "https://github.com/Happ-proxy/happ-desktop/releases/latest/download/Happ.macOS.universal.dmg",
        "hiddify_1": "https://github.com/hiddify/hiddify-next/releases/download/v2.5.7/Hiddify-MacOS.dmg",
        "v2raytun_1": "https://apps.apple.com/ru/app/v2raytun/id6476628951",
        "shadowrocket_1": "https://apps.apple.com/ru/app/shadowrocket/id932747118",
        "koalaclash_1": "https://github.com/coolcoala/clash-verge-rev-lite/releases/latest/download/Koala.Clash_x64.dmg",
        "singbox_1": "https://apps.apple.com/app/sing-box-vt/id6673731168",
        "clashverge_1": "https://github.com/clash-verge-rev/clash-verge-rev/releases/download/v2.2.2/Clash.Verge_2.2.2_x64.dmg",
        "clashverge_2": "https://github.com/clash-verge-rev/clash-verge-rev/releases/download/v2.2.2/Clash.Verge_2.2.2_aarch64.dmg"
    },
    "linux": {
        "hiddify_1": "https://github.com/hiddify/hiddify-next/releases/download/v2.5.7/Hiddify-Linux-x64.AppImage",
        "happ_1": "https://github.com/Happ-proxy/happ-desktop/releases/download/alpha_0.3.7/Happ.linux.x86.AppImage"
    }
}

# ========================================
# 🔗 ССЫЛКИ ДЛЯ АВТОМАТИЧЕСКОГО ДОБАВЛЕНИЯ
# ========================================

DEEPLINKS = {
    "happ": "happ://add/",
    "hiddify": "hiddify://import/",
    "v2raytun": "v2raytun://import/",
    "shadowrocket": "shadowrocket://add/",
    "streisand": "streisand://import/",
    "clash": "clash://install-config?url=",
    "singbox": "sing-box://import-remote-profile/?url=",
    "v2rayng": "v2rayng://install-config?url=",
    "exclave": "exclave://subscription?url="
}
