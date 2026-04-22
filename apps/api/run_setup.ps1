# Maverick Insights - Complete Database Setup
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Maverick Insights - Database Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set location
Set-Location "c:\rahul\GenAi\GEN-AI-project\apps\api"

# Step 1: Create virtual environment
Write-Host "Step 1: Creating virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path "venv")) {
    python -m venv venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Virtual environment created!" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
}

Write-Host ""

# Step 2: Upgrade pip
Write-Host "Step 2: Upgrading pip..." -ForegroundColor Yellow
.\venv\Scripts\python.exe -m pip install --upgrade pip --quiet
Write-Host "✓ Pip upgraded" -ForegroundColor Green
Write-Host ""

# Step 3: Install dependencies
Write-Host "Step 3: Installing dependencies (this may take 2-3 minutes)..." -ForegroundColor Yellow
.\venv\Scripts\python.exe -m pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ All dependencies installed!" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 4: Test database connection
Write-Host "Step 4: Testing database connection..." -ForegroundColor Yellow
.\venv\Scripts\python.exe -c "from app.database import engine; print('✅ Connected to Supabase!' if engine else '❌ Connection failed')"
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Database connection failed!" -ForegroundColor Red
    Write-Host "Please check your .env file" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Step 5: Create migration
Write-Host "Step 5: Creating migration..." -ForegroundColor Yellow
.\venv\Scripts\alembic.exe revision --autogenerate -m "Initial schema - 12 tables"
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Migration created successfully!" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to create migration" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 6: Apply migration
Write-Host "Step 6: Applying migration to Supabase..." -ForegroundColor Yellow
.\venv\Scripts\alembic.exe upgrade head
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Migration applied! 12 tables created in Supabase" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to apply migration" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 7: Seed data
Write-Host "Step 7: Seeding sample data..." -ForegroundColor Yellow
.\venv\Scripts\python.exe scripts\seed_data.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Sample data seeded successfully!" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to seed data" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ SETUP COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Verify tables in Supabase: https://aeogndsqjkbfshofudpk.supabase.co" -ForegroundColor White
Write-Host "2. Start API server: .\venv\Scripts\python.exe -m uvicorn app.main:app --reload" -ForegroundColor White
Write-Host "3. Visit API docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Login credentials:" -ForegroundColor Yellow
Write-Host "  Admin: admin@maverick.com / admin123" -ForegroundColor White
Write-Host "  HR: hr@maverick.com / hr123" -ForegroundColor White
Write-Host "  Trainer: trainer@maverick.com / trainer123" -ForegroundColor White
Write-Host "  Manager: manager@maverick.com / manager123" -ForegroundColor White
Write-Host ""
