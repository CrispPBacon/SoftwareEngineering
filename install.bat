@echo off
SETLOCAL

:: Create virtual environment
python -m venv venv

:: Install requirements
call venv\Scripts\activate.bat
pip install -r requirements.txt

:: Set Flask app and initialize migration
set FLASK_APP=flask_app.py

:: Initialize Flask-Migrate
flask db init

:: Create start.bat that activates venv and runs Flask
echo @echo off > start.bat
echo call venv\Scripts\activate.bat >> start.bat
echo set FLASK_APP=flask_app.py >> start.bat
echo flask run --port=3000 >> start.bat
echo pause >> start.bat

:: Delete this install.bat
del "%~f0"

:: Run the Flask app directly
python flask_app.py
pause
