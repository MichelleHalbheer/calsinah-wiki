@echo off

call publish\.venv\Scripts\activate.bat

python publish\content-sync.py --full-check --push

pause