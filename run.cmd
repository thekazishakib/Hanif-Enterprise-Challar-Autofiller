@echo off
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 goto usepython
py -3 challan-autofill.py
goto done
:usepython
python challan-autofill.py
:done
if errorlevel 1 pause
