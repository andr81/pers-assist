# Исправление проблемы с получением задач на сегодня

## Проблема
Метод `get_today_tasks` возвращал пустой массив, даже когда задачи на сегодня существовали в SingularityApp.

## Найденные причины (обновлено 2025-12-08)

### 1. Отсутствовал важный параметр API
API требует параметр `includeAllRecurrenceInstances=false` для корректной работы с повторяющимися задачами.

### 2. Неправильный диапазон дат
- **Было:** от начала дня до `23:59:59.999999`
- **Стало:** от начала дня до начала следующего дня (`00:00:00`)

### 3. Неправильный формат ответа
API возвращает объект `{"tasks": [...]}`, а не массив напрямую.

## Что было исправлено

### 1. api.py - добавлена поддержка нового параметра и формата ответа

**Добавлен параметр в метод list_tasks (строка ~54):**
```python
include_all_recurrence_instances: bool = False,
```

**Добавлен параметр в запрос (строка ~66):**
```python
"includeAllRecurrenceInstances": str(include_all_recurrence_instances).lower(),
```

**Исправлена обработка ответа (строки ~81-92):**
```python
# API returns {"tasks": [...]} format
if isinstance(result, dict) and 'tasks' in result:
    tasks = result['tasks']
    logger.info(f"Found {len(tasks)} tasks")
    return tasks
elif isinstance(result, list):
    # Fallback: if API returns list directly
    logger.info(f"Found {len(result)} tasks")
    return result
else:
    logger.warning(f"Unexpected response format: {type(result)}")
    return []
```

### 2. server.py - исправлен диапазон дат (строки 507-518)

**Было:**
```python
elif name == "get_today_tasks":
    from datetime import datetime
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    today_end = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999).isoformat()
    return await api.list_tasks(
        start_date_from=today_start,
        start_date_to=today_end,
    )
```

**Стало:**
```python
elif name == "get_today_tasks":
    from datetime import datetime, timedelta
    # Use full ISO 8601 format with time as required by API
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    # Use start of next day instead of end of today (matches working curl request)
    tomorrow_start = (datetime.now() + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    logger.info(f"Getting tasks for today: {today_start} to {tomorrow_start}")
    return await api.list_tasks(
        start_date_from=today_start,
        start_date_to=tomorrow_start,
        include_all_recurrence_instances=False,  # Important for recurring tasks
    )
```

## Как протестировать

### 1. Запустите тестовый скрипт
```bash
cd singularity-mcp
export SINGULARITY_API_TOKEN="ваш-токен"

# Тест исправления
python test_fix.py
```

Этот скрипт проверяет работу с правильными параметрами:
- Диапазон дат от начала сегодня до начала завтра
- Параметр includeAllRecurrenceInstances=false
- Правильная обработка формата ответа {"tasks": [...]}

### 2. Перезапустите Claude Code
После внесения изменений нужно перезапустить Claude Code, чтобы MCP сервер перезагрузился с новым кодом.

### 3. Проверьте через Claude Code
Попросите показать задачи на сегодня:
```
Покажи задачи на сегодня
```

### 4. Проверьте логи
При вызове метода в консоли MCP сервера появятся логи:
```
2025-12-08 12:00:00 - singularity_mcp.server - INFO - Tool called: get_today_tasks
2025-12-08 12:00:00 - singularity_mcp.server - INFO - Getting tasks for today: 2025-12-08T00:00:00 to 2025-12-09T00:00:00
2025-12-08 12:00:00 - singularity_mcp.api - INFO - Listing tasks with filters: project_id=None, start_date_from=2025-12-08T00:00:00, start_date_to=2025-12-09T00:00:00, include_all_recurrence_instances=False
2025-12-08 12:00:00 - singularity_mcp.api - INFO - Found 3 tasks
```

## Важные детали

### Параметры API
- **includeAllRecurrenceInstances**: должен быть `false` для получения только актуальных экземпляров повторяющихся задач
- **startDateFrom/startDateTo**: фильтруют задачи по полю `start` (дата начала задачи)
- Формат дат: полный ISO 8601 (`2025-12-08T00:00:00`)

### Формат ответа API
API возвращает:
```json
{
  "tasks": [
    {
      "id": "T-...",
      "title": "Название задачи",
      "start": "2025-12-08T10:00:00.000Z",
      ...
    }
  ]
}
```

## Рабочий пример curl-запроса
```bash
curl -X 'GET' \
  'https://api.singularity-app.com/v2/task?includeRemoved=false&includeArchived=false&includeAllRecurrenceInstances=false&startDateFrom=2025-12-08T00:00:00&startDateTo=2025-12-09T00:00:00' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```