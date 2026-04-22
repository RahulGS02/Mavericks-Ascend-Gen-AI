# Maverick Insights API

FastAPI backend for Maverick Talent Insights platform.

## Setup

### 1. Create Virtual Environment

```bash
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

### 4. Database Setup

```bash
# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial schema"

# Run migration
alembic upgrade head
```

### 5. Run Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration
│   ├── database.py          # Database connection
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── api/                 # API routes
│   │   ├── v1/
│   │   │   ├── auth.py
│   │   │   ├── mavericks.py
│   │   │   └── ...
│   ├── services/            # Business logic
│   │   ├── auth.py
│   │   ├── ai_service.py
│   │   └── ...
│   └── utils/               # Utilities
├── alembic/                 # Database migrations
├── tests/                   # Tests
└── requirements.txt
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register user
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current user

### Mavericks
- `POST /api/v1/mavericks/register` - Register maverick
- `POST /api/v1/mavericks/upload-resume` - Upload resume
- `GET /api/v1/mavericks/pending-review` - Get pending reviews

### More endpoints coming in Day 2-3...

## Testing

```bash
pytest
```

## Deployment

See deployment guide in `/docs/DEPLOYMENT.md`
