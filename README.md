Translation Microservice

A lightweight, modular, and scalable RESTful translation service built with FastAPI. Supports single & bulk translation with validation, logging, and error handling.

🚀 Features

RESTful API with FastAPI

Single & Bulk Translation

Input Validation (Pydantic)

Error Handling & Logging (SQLite)

Health Check & Statistics

Modular & Maintainable Architecture

Mock Translation (replaceable with Google Translate API)

Test Suite included

📁 Project Structure
translation-service/
├── main.py           # FastAPI app entry
├── models.py         # Pydantic models
├── config.py         # Config settings
├── requirements.txt  # Dependencies
├── services/         # Translation & logging logic
├── utils/            # Validators
└── tests/            # Unit tests

🛠 Installation
pip install -r requirements.txt
cp .env.example .env   # Fill with real values

🚀 Running

Dev:

uvicorn main:app --reload --host 0.0.0.0 --port 8000


Prod:

uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

🔌 API Endpoints

Health: GET /health

Single Translation: POST /api/v1/translate

Bulk Translation: POST /api/v1/translate/bulk

Logs & Stats: GET /api/v1/logs, GET /api/v1/logs/stats

Supported Languages: GET /api/v1/languages

🧪 Testing
pytest tests/ -v
pytest tests/ --cov=. --cov-report=html

🔧 Configuration

Switch to Google Translate by setting .env USE_GOOGLE_API=true and adding GOOGLE_API_KEY.

🗄️ Database

SQLite table translations stores logs with timestamps, character counts, and request info.

🏗 Architecture

Modular Design: Separation of concerns, single responsibility, dependency injection

Scalable: Async support, stateless, horizontal scaling

Maintainable: Type hints, Pydantic validation, logging, unit tests

🚀 Deployment (Docker)
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

🔒 Security & Performance

Input validation & sanitization

SQL parameterized queries

CORS configuration

Optional caching, rate limiting, async database

🤝 Contributing

MIT License — clean, maintainable code suitable for larger projects.
