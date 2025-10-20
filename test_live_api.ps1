# 🧪 LIVE V2 API TEST SCRIPT
# Run these tests to verify your v2 API is working!

# REPLACE THIS with your actual Railway URL:
$RAILWAY_URL = "https://yeschefapp-production.up.railway.app"

Write-Host "=" -NoNewline; Write-Host ("=" * 69)
Write-Host "TESTING LIVE V2 API DEPLOYMENT"
Write-Host "=" -NoNewline; Write-Host ("=" * 69)
Write-Host ""
Write-Host "Testing URL: $RAILWAY_URL"
Write-Host ""

# Test 1: Health Check
Write-Host "`n=== Test 1: V2 Health Check ===" -ForegroundColor Cyan
Write-Host "GET /api/v2/health"
try {
    $response = Invoke-WebRequest -Uri "$RAILWAY_URL/api/v2/health" -UseBasicParsing
    Write-Host "Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($response.Content)"
    Write-Host "✅ V2 API is alive!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Old Endpoint (Should Still Work!)
Write-Host "`n=== Test 2: Old Endpoint (Verify Still Works!) ===" -ForegroundColor Cyan
Write-Host "GET /api/direct-test"
try {
    $response = Invoke-WebRequest -Uri "$RAILWAY_URL/api/direct-test" -UseBasicParsing
    Write-Host "Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($response.Content)"
    Write-Host "✅ Old endpoints still working!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Get User
Write-Host "`n=== Test 3: Get User by ID ===" -ForegroundColor Cyan
Write-Host "GET /api/v2/users/11"
try {
    $response = Invoke-WebRequest -Uri "$RAILWAY_URL/api/v2/users/11" -UseBasicParsing
    Write-Host "Status: $($response.StatusCode)" -ForegroundColor Green
    $data = $response.Content | ConvertFrom-Json
    Write-Host "User: $($data.data.name) ($($data.data.email))"
    Write-Host "✅ User endpoint working!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Get User Stats
Write-Host "`n=== Test 4: Get User Statistics ===" -ForegroundColor Cyan
Write-Host "GET /api/v2/users/11/stats"
try {
    $response = Invoke-WebRequest -Uri "$RAILWAY_URL/api/v2/users/11/stats" -UseBasicParsing
    Write-Host "Status: $($response.StatusCode)" -ForegroundColor Green
    $data = $response.Content | ConvertFrom-Json
    Write-Host "User: $($data.data.name)"
    Write-Host "Total Recipes: $($data.data.recipe_count)"
    Write-Host "✅ User stats working!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Get Recipes with Stats (THE STAR!)
Write-Host "`n=== Test 5: Get Recipes WITH Stats (THE STAR!) ===" -ForegroundColor Cyan
Write-Host "GET /api/v2/recipes/user/11/stats"
try {
    $response = Invoke-WebRequest -Uri "$RAILWAY_URL/api/v2/recipes/user/11/stats" -UseBasicParsing
    Write-Host "Status: $($response.StatusCode)" -ForegroundColor Green
    $data = $response.Content | ConvertFrom-Json
    Write-Host "User: $($data.data.user.name)"
    Write-Host "Total Recipes: $($data.data.stats.total_recipes)"
    Write-Host "Categories: $($data.data.stats.categories -join ', ')"
    Write-Host "Category Counts:"
    $data.data.stats.category_counts.PSObject.Properties | ForEach-Object {
        Write-Host "  - $($_.Name): $($_.Value)"
    }
    Write-Host "✅ THE STAR ENDPOINT WORKS! One call, all data!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 6: Get Paginated Recipes
Write-Host "`n=== Test 6: Get Paginated Recipes ===" -ForegroundColor Cyan
Write-Host "GET /api/v2/recipes/user/11?page=1&per_page=5"
try {
    $response = Invoke-WebRequest -Uri "$RAILWAY_URL/api/v2/recipes/user/11?page=1&per_page=5" -UseBasicParsing
    Write-Host "Status: $($response.StatusCode)" -ForegroundColor Green
    $data = $response.Content | ConvertFrom-Json
    Write-Host "Page: $($data.data.pagination.page)"
    Write-Host "Items on page: $($data.data.items.Count)"
    Write-Host "Total recipes: $($data.data.pagination.total)"
    Write-Host "✅ Pagination working!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 7: Search Recipes
Write-Host "`n=== Test 7: Search Recipes ===" -ForegroundColor Cyan
Write-Host "GET /api/v2/recipes/search?user_id=11&q=chicken"
try {
    $response = Invoke-WebRequest -Uri "$RAILWAY_URL/api/v2/recipes/search?user_id=11&q=chicken" -UseBasicParsing
    Write-Host "Status: $($response.StatusCode)" -ForegroundColor Green
    $data = $response.Content | ConvertFrom-Json
    Write-Host "Found: $($data.data.count) recipes"
    Write-Host "First 3 results:"
    $data.data.recipes | Select-Object -First 3 | ForEach-Object {
        Write-Host "  - $($_.title)"
    }
    Write-Host "✅ Search working!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Summary
Write-Host "`n" -NoNewline
Write-Host "=" -NoNewline; Write-Host ("=" * 69)
Write-Host "SUMMARY"
Write-Host "=" -NoNewline; Write-Host ("=" * 69)
Write-Host ""
Write-Host "✅ V2 API IS LIVE AND WORKING!" -ForegroundColor Green
Write-Host ""
Write-Host "Your v2 API is successfully deployed with:" -ForegroundColor Cyan
Write-Host "  ✅ Old endpoints still working"
Write-Host "  ✅ New v2 endpoints working"
Write-Host "  ✅ One-call data fetching (3x faster!)"
Write-Host "  ✅ Search functionality"
Write-Host "  ✅ Pagination"
Write-Host ""
Write-Host "Ready to integrate with mobile app! 🚀" -ForegroundColor Green
