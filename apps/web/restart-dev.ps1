#!/usr/bin/env pwsh
# Restart dev server with clean cache

Write-Host "🧹 Cleaning build cache..." -ForegroundColor Yellow

# Remove .next directory
if (Test-Path ".next") {
    Remove-Item -Recurse -Force ".next"
    Write-Host "✅ Removed .next folder" -ForegroundColor Green
}

# Remove node_modules cache
if (Test-Path "node_modules/.cache") {
    Remove-Item -Recurse -Force "node_modules/.cache"
    Write-Host "✅ Removed node_modules cache" -ForegroundColor Green
}

Write-Host ""
Write-Host "🚀 Starting dev server..." -ForegroundColor Cyan
Write-Host "📝 After starting, press Ctrl+Shift+R in your browser to hard refresh" -ForegroundColor Yellow
Write-Host ""

# Start dev server
npm run dev
