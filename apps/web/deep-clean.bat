@echo off
echo ================================================
echo  MAVERICKS ASCEND - Deep Clean & Rebuild
echo ================================================
echo.
echo WARNING: This will reinstall ALL dependencies!
echo This may take 3-5 minutes.
echo.
pause

echo [1/6] Stopping any running processes...
taskkill /F /IM node.exe 2>nul
timeout /t 2 /nobreak >nul

echo [2/6] Deleting .next cache...
if exist .next rmdir /s /q .next

echo [3/6] Deleting node_modules cache...
if exist node_modules\.cache rmdir /s /q node_modules\.cache

echo [4/6] Deleting ALL node_modules...
if exist node_modules (
    echo     This may take a minute...
    rmdir /s /q node_modules
)

echo [5/6] Reinstalling dependencies...
echo     Please wait, this may take 3-5 minutes...
call npm install

echo [6/6] Starting dev server...
echo.
echo ================================================
echo  Installation complete! Starting server...
echo ================================================
echo.

npm run dev
