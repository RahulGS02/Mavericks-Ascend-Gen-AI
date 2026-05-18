@echo off
echo ================================================================================
echo           Restarting Maverick Ascend Frontend (Next.js)
echo ================================================================================
echo.

cd apps\web

echo Step 1: Cleaning Next.js cache...
if exist .next (
    rmdir /s /q .next
    echo    ✓ Removed .next folder
) else (
    echo    ✓ No .next folder to remove
)

echo.
echo Step 2: Starting Next.js dev server...
echo    URL will be: http://localhost:3000
echo.
echo    Press Ctrl+C to stop the server
echo.

npm run dev

pause
