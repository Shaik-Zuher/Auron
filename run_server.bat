@echo off
REM Navigate to the project directory (relative to the location of this batch file)
cd /d "%~dp0"

REM Check if virtual environment is activated (optional)
IF NOT DEFINED VIRTUAL_ENV (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
) ELSE (
    echo Virtual environment is already activated.
)

REM Install dependencies (if needed)
pip install -r requirements.txt

REM Run the Flask app
flask run

REM Keep the window open after execution
pause
