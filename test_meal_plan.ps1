# Test Meal Plan Creation
$RAILWAY_URL = "https://yeschefapp-production.up.railway.app"
$USER_ID = 11
$RECIPE_ID = 2690  # From our earlier test

Write-Host "Testing Meal Plan Creation..." -ForegroundColor Yellow
Write-Host ""

# Create test meal plan
$mealPlanData = @{
    user_id = $USER_ID
    plan_name = "Test Plan - " + (Get-Date -Format "MMdd-HHmmss")
    week_start_date = (Get-Date).ToString("yyyy-MM-dd")
    plan_data = @{
        monday = @{
            dinner = @{
                recipe_id = $RECIPE_ID
                title = "Test Recipe"
            }
        }
        tuesday = @{
            lunch = @{
                recipe_id = $RECIPE_ID
                title = "Test Recipe"
            }
        }
    }
} | ConvertTo-Json -Depth 10

Write-Host "Sending request..." -ForegroundColor Cyan
Write-Host "Plan Name: Test Plan - $(Get-Date -Format 'MMdd-HHmmss')" -ForegroundColor Cyan
Write-Host ""

try {
    $response = Invoke-WebRequest -Uri "$RAILWAY_URL/api/v2/meal-plans" `
        -Method POST `
        -Body $mealPlanData `
        -ContentType "application/json" `
        -UseBasicParsing
    
    Write-Host "SUCCESS!" -ForegroundColor Green
    Write-Host "Status: $($response.StatusCode)" -ForegroundColor Green
    $data = $response.Content | ConvertFrom-Json
    Write-Host "Created Plan ID: $($data.data.id)" -ForegroundColor Green
    Write-Host "Plan Name: $($data.data.plan_name)" -ForegroundColor Green
    Write-Host ""
    
    # Now test getting it back
    Write-Host "Testing GET meal plan..." -ForegroundColor Yellow
    $planId = $data.data.id
    $getResponse = Invoke-WebRequest -Uri "$RAILWAY_URL/api/v2/meal-plans/$planId`?user_id=$USER_ID" -UseBasicParsing
    $getData = $getResponse.Content | ConvertFrom-Json
    Write-Host "SUCCESS! Got plan: $($getData.data.plan_name)" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "MEAL PLAN API WORKING!" -ForegroundColor Green -BackgroundColor DarkGreen
    
} catch {
    Write-Host "FAILED!" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response: $responseBody" -ForegroundColor Red
    }
}
