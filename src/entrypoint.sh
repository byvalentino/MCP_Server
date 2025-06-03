set -e
python3 -m pip install --upgrade pip
python3 -m pip install -e src
python3 -m src/app.py