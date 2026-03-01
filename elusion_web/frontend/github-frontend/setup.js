const tg = window.Telegram.WebApp;
tg.expand();

// === НАСТРОЙКА СИСТЕМНОЙ КНОПКИ НАЗАД ===
tg.BackButton.show();
tg.BackButton.onClick(() => {
    // Укажи здесь точное имя файла главной страницы
    window.location.href = 'index.html' + window.location.search;
});

// Чтение параметров
const urlParams = new URLSearchParams(window.location.search);
const getParam = (key) => (urlParams.get(key) ? decodeURIComponent(urlParams.get(key)) : '');
const vpnKey = getParam('vpn_key');

// Ссылки
const LINKS = {
    ios: getParam('link_ios'),
    android: getParam('link_android'),
    windows: getParam('link_windows'),
    macos: getParam('link_macos'),
    manual: getParam('link_manual')
};

const platform = tg.platform || 'unknown';
let deviceName = 'устройстве';
let appName = 'Приложение';
let installLink = LINKS.manual;

function initPage() {
    if (['ios', 'ipad', 'iphone'].includes(platform)) {
        deviceName = 'iOS'; appName = 'V2RayTun'; installLink = LINKS.ios;
    } else if (platform === 'android') {
        deviceName = 'Android'; appName = 'V2RayTun'; installLink = LINKS.android;
    } else if (['tdesktop', 'weba'].includes(platform) && navigator.userAgent.indexOf('Win') !== -1) {
        deviceName = 'Windows'; appName = 'Hiddify'; installLink = LINKS.windows;
    } else if (platform === 'macos') {
        deviceName = 'macOS'; appName = 'V2RayTun'; installLink = LINKS.macos;
    }

    document.getElementById('setup-title').innerText = `Настройка на ${deviceName}`;
    document.getElementById('btn-start-text').innerText = `Начать настройку на ${deviceName}`;
}

const ICON_CLOUD_DOWN = `<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>`;

function startProcess() {
    if (!vpnKey) {
        tg.showAlert("Сначала купите подписку!");
        return;
    }
    
    tg.HapticFeedback.impactOccurred('medium');

    // 1. Анимация 33%
    document.getElementById('progress-circle').style.strokeDashoffset = '190'; 

    // 2. Иконка Облако Вниз
    document.getElementById('status-icon').innerHTML = ICON_CLOUD_DOWN;
    
    // 3. Тексты
    document.getElementById('setup-title').innerText = "Приложение";
    document.getElementById('setup-subtitle').innerHTML = `Установите приложение ${appName} <br>и вернитесь к этому экрану`;

    // 4. Кнопки (скрываем старые, показываем новые)
    document.getElementById('initial-buttons').style.display = 'none';
    document.getElementById('step-buttons-container').style.display = 'flex';
}

function performInstall() {
    tg.HapticFeedback.impactOccurred('light');
    if (installLink) tg.openLink(installLink);
    else tg.showAlert("Ссылка не найдена");
}

function nextStep() {
    tg.HapticFeedback.impactOccurred('light');
    tg.showAlert("Переход к шагу 2...");
}

function openManual() { if(LINKS.manual) tg.openLink(LINKS.manual); }

document.addEventListener('DOMContentLoaded', initPage);


// Экспорт функций для onclick
window.startProcess = startProcess;
window.performInstall = performInstall;
window.nextStep = nextStep;
window.openManual = openManual;
