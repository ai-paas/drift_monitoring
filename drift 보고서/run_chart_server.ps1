$ErrorActionPreference = "Stop"

Set-Location -LiteralPath $PSScriptRoot

& "C:\Users\jklee\anaconda3\envs\qt_env\python.exe" -u "charts\chart_selector_server.py"
