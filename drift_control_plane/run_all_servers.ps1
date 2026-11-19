$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $root

if (-not $env:LLM_INTERPRETATION_SERVER_PORT) {
    $env:LLM_INTERPRETATION_SERVER_PORT = "8767"
}

if (-not $env:CODEX_EXEC_CMD) {
    $codexCmd = Get-Command "codex.cmd" -ErrorAction SilentlyContinue
    if (-not $codexCmd) {
        $codexCmd = Get-Command "codex" -ErrorAction SilentlyContinue
    }
    if ($codexCmd) {
        $env:CODEX_EXEC_CMD = "$($codexCmd.Source) exec --sandbox read-only --skip-git-repo-check --color never"
    }
}

Start-Process -FilePath "python" -ArgumentList @("-m", "uvicorn", "admin_server.app.main:app", "--host", "127.0.0.1", "--port", "8770") -WorkingDirectory $root
Start-Process -FilePath "python" -ArgumentList @("-m", "uvicorn", "drift_server.app.main:app", "--host", "127.0.0.1", "--port", "8771") -WorkingDirectory $root
Start-Process -FilePath "python" -ArgumentList @("-m", "uvicorn", "test_feeder_server.app.main:app", "--host", "127.0.0.1", "--port", "8772") -WorkingDirectory $root
Start-Process -FilePath "python" -ArgumentList @("-u", "interpretation_server.py") -WorkingDirectory (Join-Path $repoRoot "llm_interpretation_server")

Write-Host "Admin Server:       http://127.0.0.1:8770/api/admin/health"
Write-Host "Drift Server:       http://127.0.0.1:8771/api/health"
Write-Host "Test Feeder Server: http://127.0.0.1:8772/api/test-feeder/health"
Write-Host "LLM Server:         http://127.0.0.1:8767/api/health"
