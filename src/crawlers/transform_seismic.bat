@echo off
echo 🔄 Seismic Data Transformer
echo ========================
echo.

REM Check if input file is provided
if "%~1"=="" (
    echo ❌ Error: Please provide input JSON file path
    echo Usage: transform_seismic.bat "path\to\currentPageDocs.json"
    echo.
    echo Example: transform_seismic.bat "C:\Users\username\Downloads\currentPageDocs_2025-07-21T15-20-17-195Z.json"
    pause
    exit /b 1
)

REM Set input and output file paths
set "INPUT_FILE=%~1"
set "OUTPUT_FILE=%~dpn1_transformed.json"

echo 📁 Input file:  %INPUT_FILE%
echo 📁 Output file: %OUTPUT_FILE%
echo.

REM Check if input file exists
if not exist "%INPUT_FILE%" (
    echo ❌ Error: Input file does not exist: %INPUT_FILE%
    pause
    exit /b 1
)

REM Run the Python transformation script
echo 🚀 Starting transformation...
python "%~dp0transform_seismic_data.py" "%INPUT_FILE%" "%OUTPUT_FILE%"

if %ERRORLEVEL% equ 0 (
    echo.
    echo ✅ Transformation completed successfully!
    echo 📂 Output file: %OUTPUT_FILE%
    echo.
    echo The JSON has been flattened and transformed to match the SeismicContent data model.
) else (
    echo.
    echo ❌ Transformation failed with error code %ERRORLEVEL%
)

echo.
pause