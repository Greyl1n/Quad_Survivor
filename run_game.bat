@echo off
setlocal
cd /d "%~dp0"
title Quad Survivor: The Pixel Swarm

echo ========================================================
echo        Starting Quad Survivor: The Pixel Swarm
echo ========================================================
echo.

:: 1. Check for python in PATH
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    python run_game.py
    goto check_exit
)

:: 2. Fallback to Windows Python Launcher (py)
where py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    py -3 run_game.py
    goto check_exit
)

:: 3. Fallback to common Python install locations
if exist "%LocalAppData%\Programs\Python\Python312\python.exe" (
    "%LocalAppData%\Programs\Python\Python312\python.exe" run_game.py
    goto check_exit
)

for /d %%D in ("%LocalAppData%\Programs\Python\Python3*") do (
    if exist "%%D\python.exe" (
        "%%D\python.exe" run_game.py
        goto check_exit
    )
)

echo [ERROR] Python was not found in PATH or standard install directories.
echo Please install Python (3.10+) and ensure "Add Python to PATH" is checked.
echo.
pause
exit /b 1

:check_exit
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] The game encountered an error and exited with code %ERRORLEVEL%.
    pause
)
