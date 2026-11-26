# Mini Notes API

A REST API built using FastAPI and PostgreSQL that allows users to securely create and manage personal notes.

## Features

- User registration and login
- JWT authentication
- Argon2 password hashing
- Notes CRUD operations
- User-specific data access
- Search and filtering
- Pagination
- Database migrations with Alembic
- Application logging

## Tech Stack

Python, FastAPI, PostgreSQL, SQLAlchemy, Alembic, Pydantic, JWT, Argon2.

## Project Structure

```text
app/
├── main.py
├── db.py
├── models.py
├── schemas.py
├── security.py
├── logging_config.py
└── routes/
    ├── auth.py
    └── notes.py

alembic/
README.md
pyproject.toml
```

## Setup

**1. Clone the repository**

```bash
git clone https://github.com/BuRhAn5352/Mini-Notes-App.git
cd Mini-Notes-App
```

**2. Install dependencies**

```bash
uv sync
```

**3. Configure `.env`**

```env
DATABASE_URL=your_postgresql_database_url
SECRET_KEY=your_secret_key
```

**4. Run migrations**

```bash
uv run alembic upgrade head
```

**5. Start the server**

```bash
uv run fastapi dev app/main.py
```

API documentation: `http://127.0.0.1:8000/docs`

## Author

Burhan | [GitHub](https://github.com/BuRhAn5352)