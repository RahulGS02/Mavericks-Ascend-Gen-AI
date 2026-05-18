@echo off
echo ================================================================================
echo              OCR SETUP GUIDE - Tesseract and Poppler
echo ================================================================================
echo.

echo STEP 1: Install Python OCR packages
echo ================================================================================
cd apps\api
echo Installing pytesseract, pdf2image, Pillow...
pip install pytesseract pdf2image Pillow
echo.

echo STEP 2: Check Tesseract Installation
echo ================================================================================
echo Looking for Tesseract...

set TESSERACT_PATH=
if exist "C:\Program Files\Tesseract-OCR\tesseract.exe" (
    set TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
    echo [OK] Found Tesseract at: %TESSERACT_PATH%
) else if exist "C:\Program Files (x86)\Tesseract-OCR\tesseract.exe" (
    set TESSERACT_PATH=C:\Program Files (x86)\Tesseract-OCR\tesseract.exe
    echo [OK] Found Tesseract at: %TESSERACT_PATH%
) else (
    echo [ERROR] Tesseract NOT found!
    echo.
    echo Please install from:
    echo https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe
    echo.
    echo After installation, run this script again.
    pause
    exit /b 1
)
echo.

echo STEP 3: Check Poppler Installation
echo ================================================================================
echo Looking for Poppler...

set POPPLER_PATH=
if exist "C:\poppler\Library\bin\pdftoppm.exe" (
    set POPPLER_PATH=C:\poppler\Library\bin
    echo [OK] Found Poppler at: %POPPLER_PATH%
) else if exist "C:\Program Files\poppler\Library\bin\pdftoppm.exe" (
    set POPPLER_PATH=C:\Program Files\poppler\Library\bin
    echo [OK] Found Poppler at: %POPPLER_PATH%
) else (
    echo [WARNING] Poppler NOT found!
    echo.
    echo Download from: https://github.com/oschwartz10612/poppler-windows/releases/
    echo.
    echo INSTALLATION STEPS:
    echo 1. Download "Release-XX.XX.X-0.zip"
    echo 2. Extract to C:\poppler
    echo 3. Folder structure should be: C:\poppler\Library\bin\pdftoppm.exe
    echo.
    echo After installation, run this script again.
    echo.
)

echo ================================================================================
echo STEP 4: Test OCR Setup
echo ================================================================================
echo.

if defined TESSERACT_PATH (
    echo Testing Tesseract...
    "%TESSERACT_PATH%" --version
    echo.
)

if defined POPPLER_PATH (
    echo Testing Poppler...
    "%POPPLER_PATH%\pdftoppm.exe" -v
    echo.
)

echo ================================================================================
echo SETUP SUMMARY
echo ================================================================================
echo.

if defined TESSERACT_PATH (
    echo [OK] Tesseract: INSTALLED
) else (
    echo [X] Tesseract: NOT FOUND
)

if defined POPPLER_PATH (
    echo [OK] Poppler: INSTALLED
) else (
    echo [X] Poppler: NOT FOUND - Manual setup needed
)

echo.
echo Python packages: pytesseract, pdf2image, Pillow - INSTALLED
echo.

if defined TESSERACT_PATH (
    if defined POPPLER_PATH (
        echo ================================================================================
        echo     [SUCCESS] OCR is ready! You can now process image-based PDFs!
        echo ================================================================================
    ) else (
        echo ================================================================================
        echo     [PARTIAL] Tesseract ready. Install Poppler to complete setup.
        echo ================================================================================
    )
) else (
    echo ================================================================================
    echo     [ERROR] Please install Tesseract to enable OCR
    echo ================================================================================
)

echo.
echo Press any key to continue...
pause >nul
