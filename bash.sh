uvicorn app.main:app --reload
alembic init alembic
alembic revision --autogenerate -m "Initial tables"
alembic upgrade head