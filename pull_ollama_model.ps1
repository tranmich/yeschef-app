# Pull Ollama Model on Railway
# Run this after Railway redeploys

$railwayUrl = "https://yeschefapp-production.up.railway.app"
$modelName = "llama3.2:1b"

Write-Host ""
Write-Host "📥 Pulling Ollama Model: $modelName" -ForegroundColor Cyan
Write-Host "URL: $railwayUrl" -ForegroundColor Gray
Write-Host ""
Write-Host "⏳ This will take 2-3 minutes (downloading ~1 GB)..." -ForegroundColor Yellow
Write-Host ""

$body = @{name=$modelName} | ConvertTo-Json

try {
    $response = Invoke-WebRequest `
        -Uri "$railwayUrl/api/ollama/pull-model" `
        -Method POST `
        -Body $body `
        -ContentType "application/json" `
        -TimeoutSec 300
    
    $result = $response.Content | ConvertFrom-Json
    
    if ($result.success) {
        Write-Host "✅ Success!" -ForegroundColor Green
        Write-Host "   Model: $($result.model)" -ForegroundColor White
        Write-Host "   $($result.message)" -ForegroundColor White
        Write-Host ""
        Write-Host "🎉 Model is ready! Test it now:" -ForegroundColor Green
        Write-Host "   python test_railway_deployment.py" -ForegroundColor White
    } else {
        Write-Host "❌ Failed!" -ForegroundColor Red
        Write-Host "   Error: $($result.error)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Possible issues:" -ForegroundColor Yellow
    Write-Host "   - Railway hasn't redeployed yet (wait 2-3 min)" -ForegroundColor Gray
    Write-Host "   - Network timeout (try again)" -ForegroundColor Gray
    Write-Host "   - Check Railway logs for errors" -ForegroundColor Gray
}

Write-Host ""
