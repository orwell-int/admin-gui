echo Warning! This is only starting the server! Ensure you are also starting the client in case you get an error.

call .venv\Scripts\activate.bat
@echo on
echo Start
start cmd /K python orwell\admin\app.py