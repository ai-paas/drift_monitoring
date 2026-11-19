@echo off
setlocal EnableExtensions

set "ROOT=%~dp0"
set "REPO_ROOT=%ROOT%.."
set "LLM_ROOT=%REPO_ROOT%\llm_interpretation_server"
set "PYTHON_EXE=C:\Users\jklee\anaconda3\envs\qt_env\python.exe"

cd /d "%ROOT%"

if not exist "%PYTHON_EXE%" (
  for /f "delims=" %%P in ('where python 2^>nul') do (
    set "PYTHON_EXE=%%P"
    goto :python_found
  )
)

:python_found
if not exist "%PYTHON_EXE%" (
  echo [error] Python executable not found.
  echo         Set PYTHON_EXE in this file or add python to PATH.
  exit /b 1
)

if not defined LLM_INTERPRETATION_SERVER_PORT set "LLM_INTERPRETATION_SERVER_PORT=8767"
if not defined CODEX_EXEC_CMD set "CODEX_EXEC_CMD=C:\Users\jklee\AppData\Roaming\npm\codex.cmd exec --sandbox read-only --skip-git-repo-check --color never"

if /I "%~1"=="--dry-run" (
  echo ROOT=%ROOT%
  echo PYTHON_EXE=%PYTHON_EXE%
  echo.
  echo Would start:
  echo   drift_server          http://127.0.0.1:8771/api/health
  echo   test_feeder_server    http://127.0.0.1:8772/api/test-feeder/health
  echo   llm_interpretation    http://127.0.0.1:8767/api/health
  echo   admin_server          http://127.0.0.1:8770/admin
  exit /b 0
)

echo [start] Drift control plane servers
echo [info]  Python: %PYTHON_EXE%
echo.

netstat -ano -p tcp | findstr /C:":8771 " | findstr /C:"LISTENING" >nul
if not errorlevel 1 (
  echo [skip]  drift_server already listens on 8771.
) else (
  echo [start] drift_server on 8771
  start "drift_server" /D "%ROOT%" cmd /k ""%PYTHON_EXE%" -m uvicorn drift_server.app.main:app --host 127.0.0.1 --port 8771"
)

netstat -ano -p tcp | findstr /C:":8772 " | findstr /C:"LISTENING" >nul
if not errorlevel 1 (
  echo [skip]  test_feeder_server already listens on 8772.
) else (
  echo [start] test_feeder_server on 8772
  start "test_feeder_server" /D "%ROOT%" cmd /k ""%PYTHON_EXE%" -m uvicorn test_feeder_server.app.main:app --host 127.0.0.1 --port 8772"
)

netstat -ano -p tcp | findstr /C:":8767 " | findstr /C:"LISTENING" >nul
if not errorlevel 1 (
  echo [skip]  llm_interpretation_server already listens on 8767.
) else (
  echo [start] llm_interpretation_server on 8767
  start "llm_interpretation_server" /D "%LLM_ROOT%" cmd /k ""%PYTHON_EXE%" -u interpretation_server.py"
)

netstat -ano -p tcp | findstr /C:":8770 " | findstr /C:"LISTENING" >nul
if not errorlevel 1 (
  echo [skip]  admin_server already listens on 8770.
) else (
  echo [start] admin_server on 8770
  start "admin_server" /D "%ROOT%" cmd /k ""%PYTHON_EXE%" scripts\start_admin_8770.py"
)

echo.
echo [urls]
echo   Admin UI:           http://127.0.0.1:8770/admin
echo   Admin health:       http://127.0.0.1:8770/api/admin/health
echo   Drift health:       http://127.0.0.1:8771/api/health
echo   Test feeder health: http://127.0.0.1:8772/api/test-feeder/health
echo   LLM health:         http://127.0.0.1:8767/api/health
echo.
echo If a port was skipped, the existing process is reused.
