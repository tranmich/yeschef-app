# Auto-commit script for continuous development
# Run this in PowerShell to auto-commit every 5 minutes

$repoPath = "d:\Mik\Downloads\Me Hungie"
$interval = 300 # 5 minutes in seconds

Write-Host "🤖 Auto-commit service started for: $repoPath"
Write-Host "⏰ Committing every $($interval/60) minutes"
Write-Host "🛑 Press Ctrl+C to stop"

while ($true) {
    try {
        Set-Location $repoPath
        
        # Check if there are changes
        $status = git status --porcelain
        
        if ($status) {
            $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            
            git add .
            git commit -m "🔄 Auto-commit: Development progress $timestamp"
            
            # Try to push (only if you want automatic pushing)
            # git push
            
            Write-Host "✅ [$timestamp] Auto-committed changes"
        } else {
            $timestamp = Get-Date -Format "HH:mm:ss"
            Write-Host "⏸️ [$timestamp] No changes to commit"
        }
    }
    catch {
        Write-Host "❌ Error: $($_.Exception.Message)"
    }
    
    Start-Sleep $interval
}
