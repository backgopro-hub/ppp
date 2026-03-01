# Elusion VPN API Backend

API бэкенд для управления VPN подписками с интеграцией в Telegram бота.
Фронтенд размещен на GitHub Pages: https://backgopro-hub.github.io/wp/lochi.html

## Возможности

- 🌐 FastAPI REST API бэкенд
- 📱 Интеграция с Telegram ботом через хуки
- 🔐 Rate limiting для защиты от злоупотреблений
- 📊 QR код генерация для подписок
- 🌍 Поддержка русского и английского языков
- 📺 Поддержка отправки на TV устройства
- 🔗 CORS настроен для работы с фронтендом на GitHub Pages

## Установка

1. Модуль уже находится в правильном месте (elusion_web/)

2. Установите зависимости:
```bash
pip install fastapi uvicorn qrcode[pil] httpx
```

3. Настройте конфигурацию в `settings.py`:
   - `FRONTEND_URL` - URL вашего фронтенда на GitHub Pages
   - `MODULE_PORT` - порт для API (по умолчанию 3023)
   - `API_PATH_PREFIX` - путь для API endpoints (по умолчанию /elusion/api)

4. Настройте веб-сервер (Nginx или Caddy)

### Nginx конфигурация

Добавьте в `/etc/nginx/sites-available/default`:

```nginx
location /api/ {
    proxy_pass http://localhost:3023/api/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

Примените изменения:
```bash
sudo nginx -t && sudo systemctl reload nginx
```

### Caddy конфигурация

Добавьте в `/etc/caddy/Caddyfile`:

```
reverse_proxy /api/* http://localhost:3023
```

Примените изменения:
```bash
sudo systemctl reload caddy
```

## Использование

После настройки модуль автоматически:
- Запустит API сервер на порту 3023
- Зарегистрирует хуки в боте
- Добавит кнопки в меню бота, ведущие на ваш фронтенд

Пользователи смогут:
- Открыть фронтенд через кнопку в боте
- Фронтенд будет обращаться к вашему API для получения данных

## API Endpoints

Все endpoints доступны по пути `/api/`:

- `GET /api/health` - Health check
- `GET /api/sub?key_name=X` - Получить данные подписки
- `GET /api/qr?key_name=X` - Сгенерировать QR код
- `GET /api/settings` - Получить настройки для фронтенда
- `GET /api/texts?language=ru` - Получить тексты интерфейса
- `POST /api/tv` - Отправить на TV

## Интеграция фронтенда

Ваш фронтенд на GitHub Pages должен делать запросы к API:

```javascript
// Получить данные подписки
const response = await fetch(`https://ваш-домен.com/api/sub?key_name=${keyName}`);
const data = await response.json();

// Получить QR код
const qrUrl = `https://ваш-домен.com/api/qr?key_name=${keyName}`;
```

## Версия

1.0.0
