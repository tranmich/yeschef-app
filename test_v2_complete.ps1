# COMPLETE V2 API TEST - ALL ENDPOINTS
$RAILWAY_URL = "https://yeschefapp-production.up.railway.app"
$USER_ID = 11

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "COMPLETE V2 API TEST - ALL ENDPOINTS" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

$passedTests = 0
$failedTests = 0

# TEST 1: Health Check
Write-Host "TEST 1: Health Check..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$RAILWAY_URL/api/v2/health" -UseBasicParsing
    $data = $response.Content | ConvertFrom-Json
    Write-Host "  PASS - $($data.message)" -ForegroundColor Green
    $passedTests++
} catch {
    Write-Host "  FAIL - $($_.Exception.Message)" -ForegroundColor Red
    $failedTests++
}
Write-Host ""

# TEST 2: Get User Stats
Write-Host "TEST 2: Get User Stats..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$RAILWAY_URL/api/v2/users/$USER_ID/stats" -UseBasicParsing
    $data = $response.Content | ConvertFrom-Json
    Write-Host "  PASS - User: $($data.data.name), Recipes: $($data.data.recipe_count)" -ForegroundColor Green
    $passedTests++
} catch {
    Write-Host "  FAIL - $($_.Exception.Message)" -ForegroundColor Red
    $failedTests++
}
Write-Host ""

# TEST 3: Get Recipes with Stats (THE STAR!)
Write-Host "TEST 3: Get Recipes with Stats (THE STAR!)..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$RAILWAY_URL/api/v2/recipes/user/$USER_ID/stats" -UseBasicParsing
    $data = $response.Content | ConvertFrom-Json
    Write-Host "  PASS - Got $($data.data.stats.total_recipes) recipes + categories + stats in ONE CALL!" -ForegroundColor Green
    $script:RECIPE_ID = $data.data.recipes[0].id
    Write-Host "  Sample Recipe ID: $RECIPE_ID" -ForegroundColor Cyan
    $passedTests++
} catch {
    Write-Host "  FAIL - $($_.Exception.Message)" -ForegroundColor Red
    $failedTests++
}
Write-Host ""

# TEST 4: Create Meal Plan
Write-Host "TEST 4: Create Meal Plan..." -ForegroundColor Yellow
try {
    $mealPlanData = @{
        user_id = $USER_ID
        plan_name = "Test Plan " + (Get-Date -Format "HHmmss")
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
    
    $response = Invoke-WebRequest -Uri "$RAILWAY_URL/api/v2/meal-plans" `
        -Method POST `
        -Body $mealPlanData `
        -ContentType "application/json" `
        -UseBasicParsing
    
    $data = $response.Content | ConvertFrom-Json
    $script:MEAL_PLAN_ID = $data.data.id
    Write-Host "  PASS - Created Meal Plan ID: $MEAL_PLAN_ID" -ForegroundColor Green
    $passedTests++
} catch {
    Write-Host "  FAIL - $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $errorBody = $reader.ReadToEnd()
        Write-Host "  Error Details: $errorBody" -ForegroundColor Red
    }
    $failedTests++
    $script:MEAL_PLAN_ID = $null
}
Write-Host ""

# TEST 5: Get Meal Plan
if ($null -ne $MEAL_PLAN_ID) {
    Write-Host "TEST 5: Get Meal Plan..." -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest -Uri "$RAILWAY_URL/api/v2/meal-plans/$MEAL_PLAN_ID`?user_id=$USER_ID" -UseBasicParsing
        $data = $response.Content | ConvertFrom-Json
        Write-Host "  PASS - Retrieved: $($data.data.plan_name)" -ForegroundColor Green
        $passedTests++
    } catch {
        Write-Host "  FAIL - $($_.Exception.Message)" -ForegroundColor Red
        $failedTests++
    }
    Write-Host ""
}

# TEST 6: Generate Grocery List from Meal Plan (POWER FEATURE!)
if ($null -ne $MEAL_PLAN_ID) {
    Write-Host "TEST 6: Generate Grocery List from Meal Plan (POWER FEATURE!)..." -ForegroundColor Magenta
    try {
        $response = Invoke-WebRequest -Uri "$RAILWAY_URL/api/v2/meal-plans/$MEAL_PLAN_ID/grocery-list?user_id=$USER_ID" -UseBasicParsing
        $data = $response.Content | ConvertFrom-Json
        Write-Host "  PASS - Generated $($data.data.total_ingredients) ingredients from $($data.data.recipe_count) recipes!" -ForegroundColor Green
        Write-Host "  ONE API CALL CREATED COMPLETE GROCERY LIST!" -ForegroundColor Yellow
        $passedTests++
    } catch {
        Write-Host "  FAIL - $($_.Exception.Message)" -ForegroundColor Red
        $failedTests++
    }
    Write-Host ""
}

# TEST 7: Save Grocery List from Meal Plan (POWER FEATURE!)
if ($null -ne $MEAL_PLAN_ID) {
    Write-Host "TEST 7: Save Grocery List from Meal Plan (POWER FEATURE!)..." -ForegroundColor Magenta
    try {
        $response = Invoke-WebRequest -Uri "$RAILWAY_URL/api/v2/grocery-lists/from-meal-plan/$MEAL_PLAN_ID`?user_id=$USER_ID" `
            -Method POST `
            -ContentType "application/json" `
            -UseBasicParsing
        
        $data = $response.Content | ConvertFrom-Json
        $script:GROCERY_LIST_ID = $data.data.id
        Write-Host "  PASS - Saved Grocery List ID: $GROCERY_LIST_ID with $($data.data.stats.total_items) items!" -ForegroundColor Green
        $passedTests++
    } catch {
        Write-Host "  FAIL - $($_.Exception.Message)" -ForegroundColor Red
        $failedTests++
        $script:GROCERY_LIST_ID = $null
    }
    Write-Host ""
}

# TEST 8: Get Grocery List
if ($null -ne $GROCERY_LIST_ID) {
    Write-Host "TEST 8: Get Grocery List..." -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest -Uri "$RAILWAY_URL/api/v2/grocery-lists/$GROCERY_LIST_ID`?user_id=$USER_ID" -UseBasicParsing
        $data = $response.Content | ConvertFrom-Json
        Write-Host "  PASS - Retrieved: $($data.data.name) with $($data.data.stats.total_items) items" -ForegroundColor Green
        $passedTests++
    } catch {
        Write-Host "  FAIL - $($_.Exception.Message)" -ForegroundColor Red
        $failedTests++
    }
    Write-Host ""
}

# TEST 9: Mark Item as Purchased
if ($null -ne $GROCERY_LIST_ID) {
    Write-Host "TEST 9: Mark Item as Purchased..." -ForegroundColor Yellow
    try {
        $purchaseData = @{
            user_id = $USER_ID
            purchased = $true
        } | ConvertTo-Json
        
        $response = Invoke-WebRequest -Uri "$RAILWAY_URL/api/v2/grocery-lists/$GROCERY_LIST_ID/items/0/purchase" `
            -Method POST `
            -Body $purchaseData `
            -ContentType "application/json" `
            -UseBasicParsing
        
        $data = $response.Content | ConvertFrom-Json
        $completion = [math]::Round($data.data.stats.completion_percentage, 1)
        Write-Host "  PASS - Item purchased! Progress: $($data.data.stats.purchased_items)/$($data.data.stats.total_items) ($completion%)" -ForegroundColor Green
        $passedTests++
    } catch {
        Write-Host "  FAIL - $($_.Exception.Message)" -ForegroundColor Red
        $failedTests++
    }
    Write-Host ""
}

# TEST 10: Get User Grocery Lists
Write-Host "TEST 10: Get All User Grocery Lists..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$RAILWAY_URL/api/v2/grocery-lists/user/$USER_ID" -UseBasicParsing
    $data = $response.Content | ConvertFrom-Json
    Write-Host "  PASS - Found $($data.data.stats.total_lists) grocery lists" -ForegroundColor Green
    $passedTests++
} catch {
    Write-Host "  FAIL - $($_.Exception.Message)" -ForegroundColor Red
    $failedTests++
}
Write-Host ""

# FINAL RESULTS
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "TEST RESULTS" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Passed: $passedTests" -ForegroundColor Green
Write-Host "Failed: $failedTests" -ForegroundColor $(if ($failedTests -eq 0) { "Green" } else { "Red" })
Write-Host ""

if ($failedTests -eq 0) {
    Write-Host "================================================================================" -ForegroundColor Green
    Write-Host "ALL TESTS PASSED! V2 API IS FULLY FUNCTIONAL!" -ForegroundColor Green -BackgroundColor DarkGreen
    Write-Host "================================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your complete v2 API is working:" -ForegroundColor Yellow
    Write-Host "  - Users API" -ForegroundColor Cyan
    Write-Host "  - Recipes API (THE STAR!)" -ForegroundColor Cyan
    Write-Host "  - Meal Plans API" -ForegroundColor Cyan
    Write-Host "  - Grocery Lists API" -ForegroundColor Cyan
    Write-Host "  - Power Features (Meal Plan -> Grocery List)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "READY FOR PHASE 8!" -ForegroundColor Green
} else {
    Write-Host "Some tests failed. Review errors above." -ForegroundColor Yellow
}
Write-Host ""
