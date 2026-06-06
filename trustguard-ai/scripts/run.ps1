param(
    [switch]$NoFrontend
)

Write-Host "=== TrustGuard AI ===" -ForegroundColor Cyan
Write-Host "Enterprise Reliability Platform" -ForegroundColor Cyan
Write-Host ""

$root = Split-Path -Parent $PSScriptRoot

# Start backend
Write-Host "[1/2] Starting backend (uvicorn)..." -ForegroundColor Green
$backendJob = Start-Job -Name "TrustGuard-Backend" -ScriptBlock {
    param($dir)
    Set-Location "$dir\backend"
    uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
} -ArgumentList $root

Start-Sleep -Seconds 4

if (!$NoFrontend) {
    Write-Host "[2/2] Starting frontend (vite)..." -ForegroundColor Green
    $frontendJob = Start-Job -Name "TrustGuard-Frontend" -ScriptBlock {
        param($dir)
        Set-Location "$dir\frontend"
        npm run dev
    } -ArgumentList $root
}

Write-Host ""
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Yellow
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Red

try {
    while ($true) {
        Start-Sleep -Seconds 1
        $bj = Receive-Job -Job $backendJob -Keep
        if ($bj) { Write-Host $bj }

        if (!$NoFrontend) {
            $fj = Receive-Job -Job $frontendJob -Keep
            if ($fj) { Write-Host $fj }
        }

        if ($backendJob.State -eq "Failed") {
            Write-Host "Backend failed!" -ForegroundColor Red
            Receive-Job -Job $backendJob
            break
        }
    }
} finally {
    Write-Host "Shutting down..." -ForegroundColor Yellow
    Stop-Job $backendJob -ErrorAction SilentlyContinue
    if (!$NoFrontend) {
        Stop-Job $frontendJob -ErrorAction SilentlyContinue
    }
    Remove-Job $backendJob -Force -ErrorAction SilentlyContinue
    if (!$NoFrontend) {
        Remove-Job $frontendJob -Force -ErrorAction SilentlyContinue
    }
}
