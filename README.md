# Checks
Цей проект - тестове завдання на позицію Python Backend Developer у компанію https://checkbox.ua/

Завдання знаходиться у файлі task.pdf

## Технології
Основні технології, які я використав, мали такі версії:
- Docker Desktop 4.14.1
- Docker 26.1.1
- Docker Compose 2.12.2
- Poetry 1.8.1
- PostgreSQL 16
- Python 3.12

## Підготовка до запуску
### Змінні оточення
У корені проекту створіть файл .env аналогічний цьому:
```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=postgres
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

JWT_SIGNING_ALGORITHM=RS256
JWT_LIFETIME_MINUTES=2880
```

### Конфігурація
У корені проекту створіть папку configs

#### Ключі шифрування для JWT
У папці configs створіть папку jwt</br>
Виконайте команди:
```
ssh-keygen -t rsa -b 4096 -m PEM -f jwtRS256.key
openssl rsa -in jwtRS256.key -pubout -outform PEM -out jwtRS256.key.pub
```
Отримані файли покладіть у папку configs/jwt

#### Конфіг для pgadmin4
У папці configs створіть папку pgadmin4</br>
У цій папці створіть файл servers.json аналогічний цьому:
```
{
  "Servers": {
    "1": {
      "Name": "db",
      "Group": "Servers",
      "Port": 5432,
      "Username": "postgres",
      "Host": "postgres",
      "SSLMode": "prefer",
      "MaintenanceDB": "postgres"
    }
  }
}
```
Також приклад можна знайти за посиланням: https://www.pgadmin.org/docs/pgadmin4/latest/import_export_servers.html#json-format

## Запуск
Для запуску використовується docker compose з ключем --profiles. Цей ключ контролює режими роботи. Він може приймати одне із значень:
- prod - режим для проду
- dev - режим для розробки
- migrations - режим для роботи з міграціями за допомогою alembic
- tests - режим для запуску тестів
- tests_dev - режим для запуску тестів, більш зручний для розробки тестів

Перед першим запуском у режимі prod або dev виконайте команди:
```
docker compose --profile migrations build
docker compose --profile migrations run migrations alembic upgrade head
```
Для запуску на проді виконайте:
```
docker compose --profile prod up --build
```
Для запуску тестів виконайте:
```
docker compose --profile tests up --build
```

## Для розробки
Встановіть poetry та виконайте:
```
poetry install --with dev,migrations,tests
pre-commit install
```
При кожному коміті будуть виконуватися перевірки якості коду. Якщо хоч 1 з перевірок не пройде, коміт не буде створено.
