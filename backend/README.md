## BACKEND Docs

****
*4 сентября*

Изменил апку accounts на users. Extend базового юзера.\
Обновил settings.py, добавил апки и селери cases, packs, users\
Makemigrations и migrate применять в таком порядке:
1. Packs
2. Users
3. Cases
4. Джанго модели

Добавил роутер для всех апок.\
Добавил новые зависимости.\
Добавил медиа с заглушкой для аватарки пользователя.\
Добавил сериализаторы.

Добавил в core клиент celery с beat таской которая запускается через cron раз в определенное время

**Для работы воркера:**\
`cd backend` \
`celery -A core.celery worker -l INFO`

**Для работы beatа:**\
`cd backend`\
`celery -A core.celery beat -l INFO`

`CRON_MINUTES` - сюда указывать раз в сколько минут будет запускаться таска\

****