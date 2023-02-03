@echo off
:start
cls
python -m venv text-extractor
activate

pip install -r requirements.txt

exit