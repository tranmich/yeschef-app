# YesChef Server Startup Script
# Run this to start the server with venv automatically activated

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║           YesChef Server Starting...                 ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Change to project directory
$projectPath = "D:\Mik\Downloads\Me Hungie"
Set-Location $projectPath
Write-Host "📁 Project directory: $projectPath" -ForegroundColor Green

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Check if activation worked
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Virtual environment activated!" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to activate virtual environment" -ForegroundColor Red
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Write-Host ""
Write-Host "🚀 Starting Flask server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Server will be available at:" -ForegroundColor Cyan
Write-Host "  • http://localhost:5000" -ForegroundColor White
Write-Host "  • http://192.168.1.72:5000 (from mobile devices)" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Start the server
python hungie_server.py

# If server stops, keep window open
Write-Host ""
Write-Host "Server stopped." -ForegroundColor Yellow
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
