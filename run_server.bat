@echo off
cd /d "%~dp0"

:: Check if MySQL is installed
mysql --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo ❌ MySQL is not installed or not added to PATH!
    pause
    exit /b
)

:: Check if db_config.json exists
IF EXIST db_config.json (
    echo ✅ Found database configuration.
) ELSE (
    echo 📝 No database config found. Please enter your MySQL credentials.

    set /p DB_USER=Enter your MySQL username: 
    set /p DB_PASS=Enter your MySQL password: 

    :: Save to db_config.json using pure batch
    (
        echo {
        echo     "host": "localhost",
        echo     "user": "%DB_USER%",
        echo     "password": "%DB_PASS%"
        echo }
    ) > db_config.json

    echo ✅ Database configuration saved to db_config.json
)

:: Activate virtual environment
IF EXIST .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) ELSE (
    echo ❌ Virtual environment not found. Please create it using: python -m venv .venv
    pause
    exit /b
)

:: Install dependencies
pip install -r requirements.txt

:: Train model if missing
IF NOT EXIST model.pkl (
    echo Training ML model...
    python train_model.py
)

:: Run the app
start http://127.0.0.1:5000/
flask run

pause
