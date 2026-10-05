# CarZen Backend API

FastAPI + SQLAlchemy + MySQL backend service for CarZen automotive marketplace and service management.

## Documentation Links

- **Main Repository Guide**: [../README.md](../README.md)
- **Comprehensive API Documentation**: [../docs/API_DOCUMENTATION.md](../docs/API_DOCUMENTATION.md)
- **Interactive Swagger UI**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Initialize database & create all tables (optional, run.py also auto-creates tables)
python init_db.py

# 3. Start development server
python run.py
# or:
uvicorn app.main:app --reload --port 8000
```