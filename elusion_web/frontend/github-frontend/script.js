// НОВАЯ ВЕРСИЯ script.js - только новый API
// URL бота загружается динамически через /api/settings для безопасности

// Импорт функций API
import { initializeApi, getSubscription, getQRCodeUrl, getUserKeys } from './api-integration.js';

const tg = window.Telegram.WebApp;
tg.expand();
tg.setHeaderColor('#000000');
tg.setBackgroundColor('#000000');

// Защита от ПКМ
(function() {
    document.addEventListener('contextmenu', (e) => e.preventDefault());
})();

// === ГЛАВНАЯ ФУНКЦИЯ РАСПАКОВКИ ===
function getAppData() {
    let raw = {};
    const startParam = tg.initDataUnsafe?.start_param;
    
    // 1. Если открыли как Mini App (есть start_param)
    if (startParam) {
        try {
            let base64 = startParam.replace(/-/g, '+').replace(/_/g, '/');
            while (base64.length % 4) {
                base64 += '=';
            }
            const jsonString = decodeURIComponent(escape(atob(base64)));
            raw = JSON.parse(jsonString);
            console.log("Start param data:", raw);
        } catch (e) {
            console.error("Decode error:", e);
        }
    }
    
    // 2. Если открыли просто по ссылке (резерв)
    if (Object.keys(raw).length === 0) {
        const p = new URLSearchParams(window.location.search);
        return {
            title: p.get('title'),
            userId: p.get('user_id'),
            status: p.get('status'),
            date: p.get('date'),
            vpn_key: p.get('vpn_key'),
            key_name: p.get('key_name'),
            links: {
                ios: p.get('link_ios'),
                android: p.get('link_android'),
                windows: p.get('link_windows'),
                macos: p.get('link_macos'),
                manual: p.get('link_manual'),
                support: p.get('support')
            }
        };
    }

    // 3. Возвращаем распакованный объект
    return {
        title: raw.t,
        userId: raw.u,
        status: raw.s,
        date: raw.d,
        vpn_key: raw.k,
        key_name: raw.kn,
        links: {
            ios: raw.li,
            android: raw.la,
            windows: raw.lw,
            macos: raw.lm,
            manual: raw.h,
            support: raw.sup
        }
    };
}

// Загружаем начальные данные
const appData = getAppData();

// === ЗАГРУЗКА ДАННЫХ ИЗ API ===
async function loadSubscriptionData() {
    try {
        // Инициализируем API (загружаем URL бота с сервера)
        const settings = await initializeApi();
        
        // Обновляем название приложения из настроек
        if (settings && settings.app_name) {
            updateAppName(settings.app_name);
        }
        
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
        
        console.log("Загрузка данных для key_name:", appData.key_name);
        await loadFromApi(appData.key_name);
        
    } catch (error) {
        console.error("Error loading subscription:", error);
        const statusText = document.getElementById('status-text');
        if (statusText) {
            statusText.innerText = 'Ошибка загрузки';
            statusText.style.color = '#ef4444';
        }
    }
}

// Загрузка через API
async function loadFromApi(keyName) {
    try {
        const data = await getSubscription(keyName);
        console.log("API subscription data:", data);
        
        // Форматируем дату
        const expiryDate = new Date(data.expiry);
        const formattedDate = expiryDate.toLocaleDateString('ru-RU');
        
        // Проверяем истекла ли подписка
        const now = new Date();
        const isExpired = expiryDate < now;
        
        // Обновляем UI
        const uiData = {
            status: isExpired ? 'expired' : 'active',
            date: formattedDate,
            vpn_key: data.link,
            email: data.email
        };
        
        updateSubscriptionUI(uiData);
        
        // Сохраняем для использования в других функциях
        window.currentSubscriptionData = data;
        
    } catch (error) {
        console.error("Error loading from API:", error);
        throw error;
    }
}

function updateSubscriptionUI(data) {
    const statusText = document.getElementById('status-text');
    const dateText = document.getElementById('date-text-val');
    const btnLabel = document.getElementById('btn-label');

    // Обновляем статус
    if (statusText) {
        if (data.status === 'active') {
            statusText.innerText = 'Активна';
            statusText.style.color = '#00D68F';
            if (btnLabel) btnLabel.innerText = 'Продлить подписку';
        } else {
            statusText.innerText = 'Истекла';
            statusText.style.color = '#facc15';
            if (btnLabel) btnLabel.innerText = 'Купить подписку';
        }
    }
    
    // Обновляем дату
    if (dateText && data.date) {
        dateText.innerText = data.date;
    }
    
    // Обновляем глобальный ключ для кнопок
    if (data.vpn_key) {
        appData.vpn_key = data.vpn_key;
        window.currentVpnKey = data.vpn_key;
    }
}

// === ОБНОВЛЕНИЕ ИНТЕРФЕЙСА ===
function updateAppName(appName) {
    // Обновляем title страницы
    document.title = appName;
    
    // Обновляем заголовок в интерфейсе
    const headerEl = document.getElementById('header-title');
    if (headerEl) {
        headerEl.innerText = appName;
    }
}

function updateUI() {
    // Заголовок (если передан через start_param)
    if (appData.title) {
        updateAppName(appData.title);
    }

    // Устройство
    const deviceText = document.getElementById('device-text');
    if (deviceText) {
        const platform = tg.platform || 'unknown';
        
        // Определяем устройство более точно
        if (platform === 'ios' || platform === 'ipad' || platform === 'iphone') {
            deviceText.innerText = 'iOS';
        } else if (platform === 'macos') {
            deviceText.innerText = 'macOS';
        } else if (platform === 'android') {
            deviceText.innerText = 'Android';
        } else if (platform === 'tdesktop' || platform === 'weba') {
            deviceText.innerText = 'Windows';
        } else {
            deviceText.innerText = 'Device';
        }
    }

    // Применяем данные из start_param
    if(appData.status) {
        updateSubscriptionUI({
            status: appData.status,
            date: appData.date,
            vpn_key: appData.vpn_key
        });
    }
}

// === ПЕРЕХОДЫ (КНОПКИ) ===
function openSetup() {
    const params = new URLSearchParams();
    const keyToUse = window.currentVpnKey || appData.vpn_key;
    if (keyToUse) params.append('vpn_key', keyToUse);
    
    // Передаем key_name
    if (appData.key_name) params.append('key_name', appData.key_name);
    
    if (appData.links) {
        if (appData.links.ios) params.append('link_ios', appData.links.ios);
        if (appData.links.android) params.append('link_android', appData.links.android);
        if (appData.links.windows) params.append('link_windows', appData.links.windows);
        if (appData.links.macos) params.append('link_macos', appData.links.macos);
        if (appData.links.manual) params.append('link_manual', appData.links.manual);
    }
    window.location.href = 'setup.html?' + params.toString();
}

function openSupport() {
    if (appData.links && appData.links.support) {
        tg.openLink(appData.links.support);
    } else {
        tg.showAlert("Контакты поддержки не найдены");
    }
}

function openProfile() {
    const params = new URLSearchParams();
    const keyToUse = window.currentVpnKey || appData.vpn_key;
    if (keyToUse) params.append('vpn_key', keyToUse);
    if (appData.userId) params.append('user_id', appData.userId);
    if (appData.key_name) params.append('key_name', appData.key_name);
    
    window.location.href = 'profile.html?' + params.toString();
}

function openOrder() {
    window.location.href = 'order.html' + window.location.search;
}

// === ИНИЦИАЛИЗАЦИЯ ===
document.addEventListener('DOMContentLoaded', () => {
    updateUI(); 
    loadSubscriptionData();
});

// ЭКСПОРТ
window.openSetup = openSetup;
window.openSupport = openSupport;
window.openProfile = openProfile;
window.openOrder = openOrder;
