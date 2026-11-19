@echo off
setlocal
cd /d "%~dp0"
if not defined LLM_INTERPRETATION_SERVER_PORT set "LLM_INTERPRETATION_SERVER_PORT=8767"
if not defined CODEX_EXEC_CMD set "CODEX_EXEC_CMD=C:\Users\jklee\AppData\Roaming\npm\codex.cmd exec --sandbox read-only --skip-git-repo-check --color never"
"C:\Users\jklee\anaconda3\envs\qt_env\python.exe" -u "interpretation_server.py"
