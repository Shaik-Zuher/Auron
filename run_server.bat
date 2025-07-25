@echo off
cd /d "%~dp0"

:: === Check if MySQL is installed ===
mysql --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo MySQL is not installed or not added to PATH.
    pause
    exit /b
)

:: === Check if Python is installed ===
where python >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python not found. Attempting to install...

    :: Download Python using bitsadmin
    bitsadmin /transfer pythonDownloadJob https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe "%cd%\python-installer.exe"

    IF NOT EXIST python-installer.exe (
        echo Failed to download Python installer. Please install manually:
        echo https://www.python.org/downloads/windows/
        pause
        exit /b
    )

    :: Install Python silently
    start /wait python-installer.exe /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
    del python-installer.exe

    :: Re-check Python installation
    where python >nul 2>&1
    IF %ERRORLEVEL% NEQ 0 (
        echo Python installation failed. Please install manually.
        pause
        exit /b
    )
)

:: === Check if db_config.json exists ===
IF EXIST db_config.json (
    rem Already configured
) ELSE (
    python configure_db.py
    IF EXIST db_config.json (
        rem Config created successfully
    ) ELSE (
        echo XXXXX Failed to create db_config.json
        pause
        exit /b
    )
)

:: === Create virtual environment if missing ===
IF NOT EXIST .venv (
    python -m venv .venv
    IF NOT EXIST .venv (
        echo Failed to create virtual environment.
        pause
        exit /b
    )
)

:: === Activate virtual environment ===
call .venv\Scripts\activate.bat

:: === Upgrade pip silently ===
python -m pip install --upgrade pip >nul 2>&1

:: === Install dependencies ===
echo Installing dependencies... Please wait.
pip install -r requirements.txt >nul 2>&1
echo [INFO] Dependencies installed.

:: === Train model if not already trained ===
IF NOT EXIST model.pkl (
    python model/train_model.py
)

:: === Set Flask environment ===
set FLASK_APP=app.py
set FLASK_ENV=development

:: === Message to user ===
echo.
echo 🚀 Flask server is running! Visit http://127.0.0.1:5000
echo Press CTRL+C in this window to stop the server.
echo.

:: === Open browser after short delay ===
start "" /min cmd /c "timeout /t 5 >nul && start http://127.0.0.1:5000/"
echo If site shows page not found  Refresh page after 10 seconds.
echo It takes time when starting first step.
:: === Start Flask server ===
flask run
