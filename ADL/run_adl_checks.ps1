$ErrorActionPreference = "Stop"

$cue = Join-Path $PSScriptRoot "tools\cue\cue.exe"
$java = Join-Path $PSScriptRoot "tools\java\jdk-21.0.11+10-jre\bin\java.exe"
$tlaJar = Join-Path $PSScriptRoot "tools\tla2tools.jar"
$tlaDir = Join-Path $PSScriptRoot "tla"
$runId = Get-Date -Format "yyyyMMdd-HHmmss"

if (-not (Test-Path -LiteralPath $cue)) {
    throw "CUE executable not found: $cue"
}
if (-not (Test-Path -LiteralPath $java)) {
    throw "Java executable not found: $java"
}
if (-not (Test-Path -LiteralPath $tlaJar)) {
    throw "TLA+ tools jar not found: $tlaJar"
}

Write-Host "== CUE eval =="
& $cue eval (Join-Path $PSScriptRoot "cue")

Write-Host "== TLC DriftControlPlane =="
Push-Location $tlaDir
try {
    & $java -XX:+UseParallelGC -cp "..\tools\tla2tools.jar" tlc2.TLC -metadir "states\dcp-$runId" -config "DriftControlPlane.cfg" "DriftControlPlane.tla"
}
finally {
    Pop-Location
}

Write-Host "== TLC EventAnalysisFlow =="
Push-Location $tlaDir
try {
    & $java -XX:+UseParallelGC -cp "..\tools\tla2tools.jar" tlc2.TLC -metadir "states\eaf-$runId" -config "EventAnalysisFlow.cfg" "EventAnalysisFlow.tla"
}
finally {
    Pop-Location
}
