from aiohttp import web
from .client import make_authorized_request

ACTIONS = {
    "get_profile": { "method": "GET", "url_template": "/users/{tg_id}" },
    "get_servers": { "method": "GET", "url_template": "/servers" },
    # Берем общий список (теперь это сработает без 422)
    "get_keys":    { "method": "GET", "url_template": "/keys?limit=1000" }, 
    "create_key":  { "method": "POST", "url_template": "/keys/create" }
}

async def proxy_handler(request: web.Request):
    try:
        try:
            payload = await request.json()
        except:
            return web.json_response({"error": "Bad JSON"}, status=400)
        
        action_name = payload.get("action")
        tg_id = payload.get("tg_id")
        
        # Приводим к строке для сравнения
        tg_id_str = str(tg_id)

        if not action_name: return web.json_response({"error": "No action"}, status=400)
        if action_name not in ACTIONS: return web.json_response({"error": "Denied"}, status=403)

        cfg = ACTIONS[action_name]
        # Форматируем URL только если там есть {tg_id}
        url = cfg["url_template"]
        if "{tg_id}" in url:
            url = url.format(tg_id=tg_id)

        print(f"DEBUG: Запрос -> {cfg['method']} {url}")

        # Подготовим параметры или тело запроса
        req_data = None
        if cfg["method"] == "GET":
            # Всегда пробрасываем tg_id как query-параметр, если он есть
            req_data = {"tg_id": tg_id} if tg_id is not None else None
        else:
            # Для POST-просим переслать исходный payload
            req_data = payload

        data, status = await make_authorized_request(url, cfg["method"], data=req_data)

        # === ФИЛЬТРАЦИЯ КЛЮЧЕЙ ===
        if action_name == "get_keys" and status == 200:
            print("DEBUG: Фильтрация ключей...")
            my_keys = []
            # Ищем список внутри ответа
            source_list = data if isinstance(data, list) else data.get("items", []) or data.get("keys", [])
            
            for k in source_list:
                # Ищем любые упоминания ID
                uid = str(k.get("user_id") or k.get("tg_id") or k.get("telegram_id") or "")
                if uid == tg_id_str:
                    my_keys.append(k)
            
            return web.json_response(my_keys, status=200)

        # Если ошибка, выводим её в консоль для проверки
        if status >= 400:
            print(f"DEBUG ERROR BODY: {data}")

        return web.json_response(data, status=status)

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        return web.json_response({"error": str(e)}, status=500)