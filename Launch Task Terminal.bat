@echo off
setlocal EnableExtensions

cd /d "%~dp0"
title Task Terminal Launcher
set "LOG_FILE=%~dp0launcher.log"

echo ==========================================
echo           Task Terminal Launcher
echo ==========================================
echo.
echo Task Terminal Launcher started > "%LOG_FILE%"
echo Working folder: %CD% >> "%LOG_FILE%"

where uv >nul 2>nul
if errorlevel 1 (
  echo uv was not found on PATH.
  echo.
  echo Installing uv with the official Astral Windows installer...
  echo.
  echo uv missing; starting installer. >> "%LOG_FILE%"
  powershell -NoProfile -ExecutionPolicy ByPass -Command "irm https://astral.sh/uv/install.ps1 | iex" >> "%LOG_FILE%" 2>&1
  if errorlevel 1 (
    echo [ERROR] uv installation failed.
    echo See launcher.log for details.
    goto finish
  )

  set "PATH=%USERPROFILE%\.local\bin;%USERPROFILE%\.cargo\bin;%PATH%"
  where uv >nul 2>nul
  if errorlevel 1 (
    echo [ERROR] uv installed, but it is not available in this terminal yet.
    echo Close this window and double-click the launcher again.
    echo See launcher.log for details.
    goto finish
  )
)

echo [1/4] Checking uv...
uv --version
uv --version >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
  echo [ERROR] uv is installed, but it did not run correctly.
  echo See launcher.log for details.
  goto finish
)

echo.
echo [2/4] Ensuring uv-managed Python 3.12 is available...
uv python install 3.12 >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
  echo [ERROR] uv could not install or find Python 3.12.
  echo See launcher.log for details.
  goto finish
)

echo.
echo [3/4] Verifying sqlite3 using uv-managed Python...
uv run --python 3.12 python -c "import sqlite3; print('sqlite3 OK')" >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
  echo [ERROR] sqlite3 is not working with uv-managed Python.
  echo See launcher.log for details.
  goto finish
)
echo sqlite3 OK

echo.
echo [4/4] Launching Task Terminal with uv...
echo uv will install requirements into an isolated environment if needed.
echo Use q inside the app to quit.
echo.
uv run --python 3.12 --with-requirements requirements.txt python -m task_terminal
set "APP_EXIT=%errorlevel%"
echo App exit code: %APP_EXIT% >> "%LOG_FILE%"

if not "%APP_EXIT%"=="0" (
  echo.
  echo [ERROR] App exited with an error. See launcher.log for details.
) else (
  echo.
  echo Task Terminal closed.
)

:finish
echo.
echo This window will stay open so you can read any messages.
echo Log file: "%LOG_FILE%"
pause
endlocal
