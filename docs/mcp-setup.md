# Настройка MCP серверов

Инструкции по настройке и переаутентификации MCP серверов для персонального ассистента.

## Конфигурация

Все MCP серверы настраиваются в файле `.mcp.json` в корне проекта.

```json
{
  "mcpServers": {
    "singularity": { ... },
    "google-calendar": { ... },
    "notion": { ... }
  }
}
```

---

## Google Calendar

### Первичная настройка

1. Создай OAuth credentials в Google Cloud Console
2. Сохрани файл credentials как `auth/google-calendar-key.json`
3. Добавь конфигурацию в `.mcp.json`:

```json
"google-calendar": {
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@cocal/google-calendar-mcp"],
  "env": {
    "GOOGLE_OAUTH_CREDENTIALS": "auth/google-calendar-key.json"
  }
}
```

### Переаутентификация

Если получаешь ошибку `Authentication token is invalid or expired`, выполни:

```bash
cd /Users/vita/projects/pers-assist
GOOGLE_OAUTH_CREDENTIALS=auth/google-calendar-key.json npx @cocal/google-calendar-mcp auth
```

**Что происходит:**
- Откроется браузер с формой авторизации Google
- После авторизации токен будет сохранен автоматически
- MCP сервер будет готов к использованию

**Проверка работоспособности:**
После переаутентификации попроси Claude проверить интеграцию:
```
Проверь интеграцию с Google календарем
```

---

## Singularity

### Настройка

Singularity использует API токен, который настраивается в `.mcp.json`:

```json
"singularity": {
  "command": "singularity-mcp",
  "env": {
    "SINGULARITY_API_TOKEN": "твой-токен-здесь"
  }
}
```

**Получение токена:**
1. Войди в Singularity App
2. Перейди в Settings → API
3. Скопируй токен
4. Добавь в `.mcp.json`

### Переаутентификация

Если токен истек:
1. Получи новый токен в Singularity App
2. Обнови значение в `.mcp.json`
3. Перезапусти Claude Code

---

## Notion

### Настройка

Notion использует Integration Token:

```json
"notion": {
  "command": "npx",
  "args": ["-y", "@notionhq/notion-mcp-server"],
  "env": {
    "NOTION_TOKEN": "твой-токен-здесь"
  }
}
```

**Получение токена:**
1. Перейди на https://www.notion.so/my-integrations
2. Создай новую интеграцию
3. Скопируй Internal Integration Token
4. Добавь в `.mcp.json`
5. Подключи интеграцию к нужным страницам/базам данных в Notion

### Переаутентификация

Если токен истек или был отозван:
1. Создай новый Integration Token
2. Обнови значение в `.mcp.json`
3. Убедись, что интеграция подключена к нужным страницам
4. Перезапусти Claude Code

---

## Общие проблемы

### MCP сервер не подключается

1. Проверь, что все зависимости установлены
2. Убедись, что переменные окружения правильно настроены
3. Проверь права доступа к файлам credentials
4. Перезапусти Claude Code через `/mcp` команду

### Ошибка "Authentication token is invalid or expired"

- Для Google Calendar: выполни переаутентификацию (см. выше)
- Для Singularity/Notion: обнови токен в `.mcp.json`

### Переменная окружения не найдена

Убедись, что пути к файлам указаны относительно корня проекта:
- ✅ `auth/google-calendar-key.json`
- ❌ `/Users/vita/projects/pers-assist/auth/google-calendar-key.json`
