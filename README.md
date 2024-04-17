# Описание

Проект YaMDb собирает отзывы пользователей на произведения.

# Авторы проекта

[Mikhail](https://github.com/tooMike)
[Elvira](https://github.com/Elyablack)

# Установка

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/tooMike/api_yamdb
```

```
cd api_yamdb
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```

# Спецификация

При локальном запуске документация будет доступна по адресу:

```
http://127.0.0.1:8000/redoc/
```

# Основные технические требования

Python==3.9.18

Django==3.2.16

djoser==2.1.0

pytest==6.2.4



# Примеры запросов к API

### Регистрация нового пользователя

Описание метода: Получить код подтверждения на переданный email. Права доступа: Доступно без токена. Использовать имя 'me' в качестве username запрещено. Поля email и username должны быть уникальными. Должна быть возможность повторного запроса кода подтверждения.

Тип запроса: `POST`

Эндпоинт: `api/v1/auth/signup/`

Обязательные параметры: `email, username`

Пример запрос:

```
{
"email": "user@example.com",
"username": "string"
}
```


Пример успешного ответа:

```
{
  "email": "string",
  "username": "string"
}
```

### Получение JWT-токена

Описание метода: Получение JWT-токена в обмен на username и confirmation code. Права доступа: Доступно без токена.

Тип запроса: `POST`

Эндпоинт: `api/v1/auth/token.`

Обязательные параметры: `username, confirmation_code`

Пример запроса:

```
{
  "username": "string",
  "confirmation_code": "string"
}
```

Пример успешного ответа:

```
{
  "token": "string"
}
```

### Добавление нового отзыва

Описание метода: Добавить новый отзыв. Пользователь может оставить только один отзыв на произведение. Права доступа: Аутентифицированные пользователи.

Тип запроса: `POST`

Эндпоинт: `/api/v1/titles/{title_id}/reviews/`

Обязательные параметры: `text, score`

Пример запроса:

```
{
  "text": "string",
  "score": 1
}
```

Пример успешного ответа:

```
{
  "id": 0,
  "text": "string",
  "author": "string",
  "score": 1,
  "pub_date": "2019-08-24T14:15:22Z"
}
```