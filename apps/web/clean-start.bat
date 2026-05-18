@echo off
echo ================================================
echo  MAVERICKS ASCEND - Clean Start Script
echo ================================================
echo.

echo [1/5] Stopping any running dev server...
taskkill /F /IM node.exe 2>nul
timeout /t 2 /nobreak >nul

echo [2/5] Cleaning Next.js cache...
if exist .next (
    rmdir /s /q .next
    echo     - Deleted .next folder
) else (
    echo     - .next folder not found
)

if exist node_modules\.cache (
    rmdir /s /q node_modules\.cache
    echo     - Deleted node_modules cache
) else (
    echo     - node_modules cache not found
)

echo [3/5] Verifying environment variables...
echo     NEXT_PUBLIC_API_URL should be: http://localhost:8000/api/v1
echo     Check .env.local file to confirm
echo.

echo [4/5] Cleaning browser cache recommendation...
echo.
echo     IMPORTANT: After server starts, do ONE of these:
echo     - Press Ctrl+Shift+R (Hard Refresh)
echo     - Or open in Incognito/Private mode
echo     - Or clear browser cache manually
echo.

echo [5/5] Starting development server...
echo.
echo ================================================
echo  Server starting... Please wait...
echo ================================================
echo.

npm run dev
