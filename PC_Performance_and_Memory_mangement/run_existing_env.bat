@echo off
cd /d "%~dp0"
if exist .venv\Scripts\python.exe (
  .venv\Scripts\python.exe -m src.main
) else (
  py -m src.main
)
pause
