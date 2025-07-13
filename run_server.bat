@echo off
REM Navigate to the project directory (relative to the location of this batch file)
cd /d "%~dp0"

REM Activate virtual environment (if not already activated)
IF NOT DEFINED VIRTUAL_ENV (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
) ELSE (
    echo Virtual environment is already activated.
)

REM Install dependencies (if needed)
pip install -r requirements.txt

REM Check if model.pkl exists
IF NOT EXIST model.pkl (
    echo model.pkl not found. Training model...
    python train_model.py
) ELSE (
    echo model.pkl found. Skipping training.
)

REM Run the Flask app
flask run

REM Keep the window open after execution
pause
