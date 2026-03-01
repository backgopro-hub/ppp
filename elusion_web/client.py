import aiohttp
from . import settings

async def make_authorized_request(endpoint: str, method="GET", data=None):
    """Шлет запрос в Netelusion с правильными заголовками"""
    
    # 1. Базовые заголовки (без Content-Type!)
    token = settings.API_TOKEN

    # Базовые заголовки — будем пробовать разные варианты при 401
    base_accept = {"Accept": "application/json"}

    # Список кандидатов заголовков в порядке приоритета
    header_variants = [
        {**base_accept, "Authorization": f"Bearer {token}", "X-Token": token},
        {**base_accept, "X-Token": token},
        {**base_accept, "Authorization": f"Token {token}", "X-Token": token},
        {**base_accept, "Authorization": token, "X-Token": token},
    ]
    
    # 2. Добавляем Content-Type ТОЛЬКО если это POST (когда мы реально шлем данные)
    if method == "POST":
        headers["Content-Type"] = "application/json"
    
    # Убираем лишний слеш в начале пути, если он есть
    if endpoint.startswith("/"):
        endpoint = endpoint[1:]
        
    url = f"{settings.API_BASE_URL}/{endpoint}"

    def _mask(val: str) -> str:
        try:
            t = token
            if not t:
                return val
            if isinstance(val, str) and t in val:
                return val.replace(t, f"***{t[-4:]}")
            if val == t:
                return f"***{t[-4:]}"
        except Exception:
            pass
        return val

    
    async with aiohttp.ClientSession() as session:
        try:
            last_data = None
            last_status = None

            # Для POST добавляем Content-Type в варианты
            if method == "POST":
                for h in header_variants:
                    h.update({"Content-Type": "application/json"})

            for hdrs in header_variants:
                masked = {k: _mask(v) for k, v in hdrs.items()}
                print(f"DEBUG HTTP -> {method} {url} headers={masked} params={data}")

                if method == "GET":
                    async with session.get(url, headers=hdrs, params=data) as resp:
                        try:
                            last_data, last_status = await resp.json(), resp.status
                        except:
                            last_data, last_status = {"error": await resp.text()}, resp.status

                elif method == "POST":
                    async with session.post(url, headers=hdrs, json=data) as resp:
                        try:
                            last_data, last_status = await resp.json(), resp.status
                        except:
                            last_data, last_status = {"error": await resp.text()}, resp.status

                else:
                    return {"error": "Method not allowed"}, 405

                # Если не 401 — возвращаем результат сразу
                if last_status != 401:
                    return last_data, last_status

            # Все варианты вернули 401 — вернуть последний ответ
            return last_data, last_status
        except Exception as e:
            return {"error": str(e)}, 500