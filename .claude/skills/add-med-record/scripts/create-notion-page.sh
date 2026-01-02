#!/bin/bash
set -e

DATABASE_ID="$1"
PAGE_TITLE="$2"

# Валидация аргументов
if [ -z "$DATABASE_ID" ] || [ -z "$PAGE_TITLE" ]; then
    echo "Usage: $0 <database_id> <page_title>" >&2
    exit 1
fi

# Проверка NOTION_TOKEN
if [ -z "$NOTION_TOKEN" ]; then
    echo "Error: NOTION_TOKEN not set" >&2
    exit 1
fi

# Создание страницы
RESPONSE=$(curl -s -X POST 'https://api.notion.com/v1/pages' \
  -H "Authorization: Bearer ${NOTION_TOKEN}" \
  -H 'Content-Type: application/json' \
  -H 'Notion-Version: 2022-06-28' \
  --data "{
    \"parent\": {\"database_id\": \"${DATABASE_ID}\"},
    \"properties\": {
      \"Name\": {
        \"title\": [{\"text\": {\"content\": \"${PAGE_TITLE}\"}}]
      }
    }
  }")

# Извлечение page_id
PAGE_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

if [ -z "$PAGE_ID" ]; then
    echo "Error: Failed to create page" >&2
    echo "Response: $RESPONSE" >&2
    exit 1
fi

echo "$PAGE_ID"
