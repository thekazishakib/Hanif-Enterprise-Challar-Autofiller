@echo off
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 goto usepython
py -3 -m pip install -r requirements.txt
goto done
:usepython
python -m pip install -r requirements.txt
:done
echo.
echo If installation succeeded, open run.cmd next.
pause
