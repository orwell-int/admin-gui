choco install -y python3
python -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install pip --upgrade
pip install -r requirements.txt