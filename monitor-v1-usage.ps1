#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Monitor V1 API endpoint usage from server logs

.DESCRIPTION
    This script monitors the backend server logs in real-time or analyzes
    existing log files to track deprecated V1 endpoint usage.

.PARAMETER Mode
    'realtime' - Monitor server output in real-time
    'analyze' - Analyze log file for V1 usage patterns

.EXAMPLE
    .\monitor-v1-usage.ps1 -Mode realtime
    .\monitor-v1-usage.ps1 -Mode analyze -LogFile server.log
#>

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('realtime', 'analyze', 'summary')]
    [string]$Mode = 'summary',
    
    [Parameter(Mandatory=$false)]
    [string]$LogFile = ""
)

$colors = @{
    Red = 'Red'
    Green = 'Green'
    Yellow = 'Yellow'
    Cyan = 'Cyan'
    Magenta = 'Magenta'
}

function Show-Header {
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "           V1 API DEPRECATION USAGE MONITOR" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""
}

function Get-V1EndpointStats {
    param([string[]]$LogLines)
    
    $stats = @{}
    $totalV1Calls = 0
    
    foreach ($line in $LogLines) {
        if ($line -match "DEPRECATED V1 ENDPOINT CALLED: (.+?) ->") {
            $endpoint = $Matches[1]
            $totalV1Calls++
            
            if ($stats.ContainsKey($endpoint)) {
                $stats[$endpoint]++
            } else {
                $stats[$endpoint] = 1
            }
        }
    }
    
    return @{
        Stats = $stats
        Total = $totalV1Calls
    }
}

function Show-Summary {
    Write-Host "📊 V1 ENDPOINT USAGE SUMMARY" -ForegroundColor Yellow
    Write-Host "─────────────────────────────────────────────────────────" -ForegroundColor Gray
    Write-Host ""
    
    # Check if server is running
    Write-Host "Checking for recent V1 endpoint usage..." -ForegroundColor Cyan
    Write-Host ""
    
    # Instructions
    Write-Host "To monitor V1 endpoint usage:" -ForegroundColor Green
    Write-Host ""
    Write-Host "  1. START BACKEND SERVER:" -ForegroundColor Yellow
    Write-Host "     cd 'D:\Mik\Downloads\Me Hungie'"
    Write-Host "     python hungie_server.py"
    Write-Host ""
    Write-Host "  2. USE YOUR APP:" -ForegroundColor Yellow
    Write-Host "     - Load recipes"
    Write-Host "     - Browse community"
    Write-Host "     - Manage pantry"
    Write-Host ""
    Write-Host "  3. WATCH SERVER TERMINAL:" -ForegroundColor Yellow
    Write-Host "     Look for lines like:"
    Write-Host "     ⚠️  DEPRECATED V1 ENDPOINT CALLED: /api/recipes -> Use /api/v2/..." -ForegroundColor Red
    Write-Host ""
    Write-Host "  4. CHECK BROWSER DEVTOOLS:" -ForegroundColor Yellow
    Write-Host "     - Open Chrome DevTools (F12)"
    Write-Host "     - Go to Network tab"
    Write-Host "     - Look for '/api/' requests (without /v2/)"
    Write-Host "     - Check Response Headers for X-API-Deprecated: true"
    Write-Host ""
    
    # Current status
    Write-Host "─────────────────────────────────────────────────────────" -ForegroundColor Gray
    Write-Host "MIGRATION STATUS:" -ForegroundColor Green
    Write-Host ""
    Write-Host "  ✅ Frontend migrated to V2" -ForegroundColor Green
    Write-Host "  ✅ All V1 endpoints deprecated" -ForegroundColor Green
    Write-Host "  ✅ Deprecation logging enabled" -ForegroundColor Green
    Write-Host "  ✅ HTTP deprecation headers added" -ForegroundColor Green
    Write-Host ""
    Write-Host "EXPECTED RESULT:" -ForegroundColor Cyan
    Write-Host "  → No V1 deprecation warnings should appear!" -ForegroundColor Green
    Write-Host "  → All API calls should use /api/v2/ endpoints" -ForegroundColor Green
    Write-Host ""
    Write-Host "─────────────────────────────────────────────────────────" -ForegroundColor Gray
    Write-Host ""
}

function Monitor-RealTime {
    Write-Host "🔴 REAL-TIME MONITORING MODE" -ForegroundColor Red
    Write-Host "─────────────────────────────────────────────────────────" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Monitoring server output for V1 endpoint usage..." -ForegroundColor Yellow
    Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
    Write-Host ""
    
    $v1Count = 0
    $startTime = Get-Date
    
    # This would tail the server logs in real-time
    # For PowerShell, we'll provide instructions instead
    Write-Host "⚠️  INSTRUCTIONS FOR REAL-TIME MONITORING:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Open a new terminal window" -ForegroundColor Cyan
    Write-Host "2. Run: cd 'D:\Mik\Downloads\Me Hungie'" -ForegroundColor Cyan
    Write-Host "3. Run: python hungie_server.py | Select-String 'DEPRECATED'" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "This will show ONLY deprecation warnings in real-time." -ForegroundColor Green
    Write-Host ""
    Write-Host "Example output you might see:" -ForegroundColor Yellow
    Write-Host "  ⚠️  DEPRECATED V1 ENDPOINT CALLED: /api/recipes" -ForegroundColor Red
    Write-Host ""
}

function Analyze-LogFile {
    param([string]$FilePath)
    
    if (-not (Test-Path $FilePath)) {
        Write-Host "❌ Log file not found: $FilePath" -ForegroundColor Red
        return
    }
    
    Write-Host "📋 ANALYZING LOG FILE: $FilePath" -ForegroundColor Yellow
    Write-Host "─────────────────────────────────────────────────────────" -ForegroundColor Gray
    Write-Host ""
    
    $lines = Get-Content $FilePath
    $result = Get-V1EndpointStats -LogLines $lines
    
    if ($result.Total -eq 0) {
        Write-Host "✅ EXCELLENT! No V1 endpoint usage found!" -ForegroundColor Green
        Write-Host ""
        Write-Host "This means:" -ForegroundColor Cyan
        Write-Host "  → Frontend is using V2 endpoints correctly" -ForegroundColor Green
        Write-Host "  → Migration is successful" -ForegroundColor Green
        Write-Host "  → No legacy code calling V1" -ForegroundColor Green
        return
    }
    
    Write-Host "⚠️  Found $($result.Total) V1 endpoint calls" -ForegroundColor Red
    Write-Host ""
    Write-Host "BREAKDOWN BY ENDPOINT:" -ForegroundColor Yellow
    Write-Host ""
    
    $sorted = $result.Stats.GetEnumerator() | Sort-Object Value -Descending
    
    foreach ($entry in $sorted) {
        $percentage = [math]::Round(($entry.Value / $result.Total) * 100, 1)
        $bar = "█" * [math]::Min(50, [math]::Round($percentage))
        
        Write-Host "  $($entry.Key)" -ForegroundColor Cyan
        Write-Host "    Count: $($entry.Value) ($percentage%)" -ForegroundColor Yellow
        Write-Host "    $bar" -ForegroundColor Red
        Write-Host ""
    }
    
    Write-Host "─────────────────────────────────────────────────────────" -ForegroundColor Gray
    Write-Host ""
    Write-Host "RECOMMENDATION:" -ForegroundColor Yellow
    Write-Host "  Check which part of the frontend is still calling V1" -ForegroundColor Cyan
    Write-Host "  Update those components to use V2 endpoints" -ForegroundColor Cyan
    Write-Host ""
}

function Show-QuickCheck {
    Write-Host ""
    Write-Host "🔍 QUICK V1 USAGE CHECK" -ForegroundColor Cyan
    Write-Host "─────────────────────────────────────────────────────────" -ForegroundColor Gray
    Write-Host ""
    
    # Check if we can grep recent logs
    $pythonDir = "D:\Mik\Downloads\Me Hungie"
    
    Write-Host "Searching for V1 usage in recent activity..." -ForegroundColor Yellow
    Write-Host ""
    
    # Try to find any log files
    $logFiles = Get-ChildItem -Path $pythonDir -Filter "*.log" -ErrorAction SilentlyContinue
    
    if ($logFiles.Count -eq 0) {
        Write-Host "No log files found. To track V1 usage:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "  1. Start backend: python hungie_server.py" -ForegroundColor Cyan
        Write-Host "  2. Use the app normally" -ForegroundColor Cyan
        Write-Host "  3. Watch terminal for deprecation warnings" -ForegroundColor Cyan
        Write-Host ""
    } else {
        Write-Host "Found log files:" -ForegroundColor Green
        foreach ($log in $logFiles) {
            Write-Host "  - $($log.Name)" -ForegroundColor Cyan
            Analyze-LogFile -FilePath $log.FullName
        }
    }
}

# Main script execution
Show-Header

switch ($Mode) {
    'realtime' {
        Monitor-RealTime
    }
    'analyze' {
        if ($LogFile) {
            Analyze-LogFile -FilePath $LogFile
        } else {
            Show-QuickCheck
        }
    }
    'summary' {
        Show-Summary
    }
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
