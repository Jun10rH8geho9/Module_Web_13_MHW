Запуск uvicorn
uvicorn main:app --host localhost --port 8000 --reload

запуск html
http://127.0.0.1:8000/docs

poetry shell

ініціалізування оточення alembic
alembic init migrations

Створюємо міграцію наступною консольною командою в корені проекту.
alembic revision --autogenerate -m 'Init'

застосуємо створену міграцію:
alembic upgrade head

poetry export --without-hashes --format=requirements.txt > requirements.txt
poetry export -f requirements.txt --output requirements.txt

docker run --name some-postgres -p 5432:5432 -e POSTGRES_PASSWORD=mysecretpassword -d postgres
docker run --name redis-name -d -p 6379:6379 redis
docker-compose up -d
docker-compose down
