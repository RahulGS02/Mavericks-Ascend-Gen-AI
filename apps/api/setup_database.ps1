# Maverick Insights - Database Setup Script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Maverick Insights - Database Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✓ Virtual environment created!" -ForegroundColor Green
    Write-Host ""
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✓ Dependencies installed!" -ForegroundColor Green

# Test database connection
Write-Host ""
Write-Host "Testing database connection..." -ForegroundColor Yellow
python -c "from app.database import engine; print('✅ Connected to Supabase!' if engine else '❌ Connection failed')"
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Database connection failed" -ForegroundColor Red
    Write-Host "Please check your .env file" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Create migration
Write-Host ""
Write-Host "Creating migration..." -ForegroundColor Yellow
alembic revision --autogenerate -m "Initial schema - 12 tables"
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to create migration" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✓ Migration created!" -ForegroundColor Green

# Apply migration
Write-Host ""
Write-Host "Applying migration to database..." -ForegroundColor Yellow
alembic upgrade head
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to apply migration" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✓ Migration applied!" -ForegroundColor Green

# Seed data
Write-Host ""
Write-Host "Seeding sample data..." -ForegroundColor Yellow
python scripts/seed_data.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to seed data" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ DATABASE SETUP COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your database is ready with:" -ForegroundColor White
Write-Host "  • 12 tables created" -ForegroundColor White
Write-Host "  • 4 users (admin, hr, trainer, manager)" -ForegroundColor White
Write-Host "  • 5 sample mavericks" -ForegroundColor White
Write-Host "  • 1 training pipeline" -ForegroundColor White
Write-Host "  • 1 active batch" -ForegroundColor White
Write-Host ""
Write-Host "Login credentials:" -ForegroundColor Yellow
Write-Host "  Admin:   admin@maverick.com / admin123" -ForegroundColor White
Write-Host "  HR:      hr@maverick.com / hr123" -ForegroundColor White
Write-Host "  Trainer: trainer@maverick.com / trainer123" -ForegroundColor White
Write-Host "  Manager: manager@maverick.com / manager123" -ForegroundColor White
Write-Host ""
Write-Host "Next: Start the API server with:" -ForegroundColor Yellow
Write-Host "  uvicorn app.main:app --reload" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to exit"
