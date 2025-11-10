@ECHO off

REM Activate the virtual environment
CALL venvv\venv\Scripts\activate

REM Start the Django development server
start /min python manage.py runserver

REM Start the npm project
start /min npm run myproject

REM Deactivate the virtual environment after use (optional)
deactivate
