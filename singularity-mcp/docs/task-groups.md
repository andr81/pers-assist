# Task Groups (Секции проектов) в SingularityApp

## Проблема

Задачи в SingularityApp требуют **два** поля для корректного отображения в проектах:
- `projectId` - ID проекта (формат: `P-{uuid}`)
- `group` - ID секции внутри проекта (формат: `Q-{uuid}`)

Если указать только `projectId` без `group`, задача **не будет отображаться** в проекте в мобильном приложении!

## Как работает API

### Автоматическое определение group

MCP сервер автоматически получает `group` через API `/v2/task-group`:

1. При создании/обновлении задачи с `project_id`
2. Запрашивает список task-groups для проекта
3. Берет первую группу (обычно дефолтная)
4. Кэширует результат для оптимизации

### API Эндпоинты

**GET /v2/task-group**
- Параметры: `parent` (project ID), `maxCount`
- Возвращает список секций проекта

**POST /v2/task-group**
- Создать новую секцию в проекте
- Поля: `title`, `parent` (project ID)

## Примеры использования

### Создать задачу в проекте

```python
# group определится автоматически через API
mcp__singularity__create_task(
    title="Купить молоко",
    project_id="P-6868b846-5c1d-49ee-8ab9-2376f8800968"
)
```

### Переместить задачу в проект

```python
# group определится автоматически
mcp__singularity__update_task(
    task_id="T-xxx",
    project_id="P-6868b846-5c1d-49ee-8ab9-2376f8800968"
)
```

### Явно указать group

```python
mcp__singularity__create_task(
    title="Купить молоко",
    project_id="P-6868b846-5c1d-49ee-8ab9-2376f8800968",
    group="Q-e7bb241d-b6c8-4907-b388-15dfb6bee33b"
)
```

### Получить список секций проекта

```python
mcp__singularity__list_task_groups(
    project_id="P-6868b846-5c1d-49ee-8ab9-2376f8800968"
)
```

### Получить дефолтную секцию

```python
mcp__singularity__get_default_task_group(
    project_id="P-6868b846-5c1d-49ee-8ab9-2376f8800968"
)
```

## Исправление задач без group

Задачи без `group` можно исправить вручную:

```python
# 1. Получить group для проекта
group_id = mcp__singularity__get_default_task_group(
    project_id="P-6868b846-5c1d-49ee-8ab9-2376f8800968"
)

# 2. Обновить задачу
mcp__singularity__update_task(
    task_id="T-a881184f-b49c-4f91-a96d-8ef1c43e1448",
    group=group_id
)
```

## Кэширование

API клиент кэширует маппинг `projectId → groupId` в памяти:
- Первый запрос для проекта идет в API
- Последующие запросы используют кэш
- Кэш сбрасывается при перезапуске MCP сервера

## Официальная документация

- Основная документация: https://singularity-app.ru/wiki/api/
- Swagger UI: https://api.singularity-app.com/v2/api
- Эндпоинт task-group: `/v2/task-group` (GET/POST/PATCH/DELETE)

## Структура данных

### Task Group Object

```json
{
  "id": "Q-e7bb241d-b6c8-4907-b388-15dfb6bee33b",
  "title": "Название секции",
  "parent": "P-6868b846-5c1d-49ee-8ab9-2376f8800968"
}
```

### Task Object (с проектом)

```json
{
  "id": "T-xxx",
  "title": "Задача",
  "projectId": "P-6868b846-5c1d-49ee-8ab9-2376f8800968",
  "group": "Q-e7bb241d-b6c8-4907-b388-15dfb6bee33b"
}
```
