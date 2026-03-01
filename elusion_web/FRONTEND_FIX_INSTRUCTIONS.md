# Инструкция по исправлению фронтенда

## Проблема
WebApp показывает "Нет данных" потому что бот не передает `key_name` в URL.

## Решение
Добавить автоматическое получение ключей пользователя через API `/api/keys/all/{tg_id}`.

---

## Файл 1: `api-integration.js`

### Добавить новую функцию после `getSubscription` (после строки ~99):

```javascript
/**
 * Получает все ключи пользователя по Telegram ID
 * @param {number} tgId - Telegram ID пользователя
 * @returns {Promise<Array>} Массив ключей пользователя
 */
export async function getUserKeys(tgId) {
    try {
        const response = await fetch(`${BOT_DOMAIN}/api/keys/all/${tgId}`);
        
        if (response.status === 404) {
            return [];
        }
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const keys = await response.json();
        console.log('[API] Got user keys:', keys);
        return Array.isArray(keys) ? keys : [];
    } catch (error) {
        console.error('[API] Error getting user keys:', error);
        return [];
    }
}
```

### Обновить экспорт в конце файла (строка ~210):

Найти:
```javascript
export const ApiIntegration = {
    initializeApi,
    getSubscription,
    getQRCodeUrl,
    getSettings,
    getTexts,
    sendToTV,
    checkHealth
};
```

Заменить на:
```javascript
export const ApiIntegration = {
    initializeApi,
    getSubscription,
    getUserKeys,  // ← ДОБАВИТЬ ЭТУ СТРОКУ
    getQRCodeUrl,
    getSettings,
    getTexts,
    sendToTV,
    checkHealth
};
```

---

## Файл 2: `script.js`

### 1. Обновить импорт (строка 4):

Найти:
```javascript
import { initializeApi, getSubscription, getQRCodeUrl } from './api-integration.js';
```

Заменить на:
```javascript
import { initializeApi, getSubscription, getQRCodeUrl, getUserKeys } from './api-integration.js';
```

### 2. Обновить функцию `loadSubscriptionData` (строка ~85-110):

Найти блок:
```javascript
// Проверяем наличие key_name
if (!appData.key_name) {
    console.warn("No key_name available");
    const statusText = document.getElementById('status-text');
    if (statusText) {
        statusText.innerText = 'Нет данных';
        statusText.style.color = '#999';
    }
    return;
}
```

Заменить на:
```javascript
// Проверяем наличие key_name
// Если key_name нет, пробуем получить из API по tg_id
if (!appData.key_name) {
    console.warn("No key_name in URL, trying to get from API");
    const tgId = tg.initDataUnsafe?.user?.id;
    
    if (tgId) {
        const keys = await getUserKeys(tgId);
        if (keys && keys.length > 0) {
            // Ищем первый не-VLESS ключ
            let targetKey = keys.find(k => !k.key || !k.key.toLowerCase().startsWith('vless://'));
            if (!targetKey) targetKey = keys[0];
            
            appData.key_name = targetKey.email || targetKey.id;
            console.log("Got key_name from API:", appData.key_name);
        }
    }
}

// Если все еще нет key_name, показываем сообщение
if (!appData.key_name) {
    console.warn("No key_name available");
    const statusText = document.getElementById('status-text');
    if (statusText) {
        statusText.innerText = 'Откройте через кнопку в боте';
        statusText.style.color = '#999';
    }
    return;
}
```

---

## Как применить изменения

1. Откройте репозиторий на GitHub: https://github.com/backgopro-hub/wp
2. Отредактируйте файл `api-integration.js`:
   - Добавьте функцию `getUserKeys`
   - Обновите экспорт
3. Отредактируйте файл `script.js`:
   - Обновите импорт
   - Замените блок проверки key_name
4. Сохраните изменения (commit)
5. GitHub Pages автоматически обновится через 1-2 минуты

---

## Что это исправит

✅ WebApp будет автоматически получать первый ключ пользователя по его Telegram ID
✅ Дата подписки будет показываться правильно (код уже есть, просто не вызывался)
✅ Статус "Истекла" будет показываться для истекших подписок (код уже есть)
✅ Работает для пользователей с несколькими подписками (берет первый не-VLESS ключ)
✅ Не требует изменений в боте

---

## Проверка

После применения изменений:
1. Откройте WebApp через бота
2. В консоли браузера должно появиться:
   - `[API] Got user keys: [...]`
   - `Got key_name from API: user@example.com`
   - `Загрузка данных для key_name: user@example.com`
   - `API subscription data: {...}`
3. На экране должна показаться дата подписки и статус
