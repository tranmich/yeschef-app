# Root Directory Cleanup Script
# Organizes test files, docs, and utility scripts

Write-Host "🧹 Starting Root Directory Cleanup..." -ForegroundColor Cyan

# Navigate to project root
Set-Location "d:\Mik\Downloads\Me Hungie"

# ============================================
# 1. DELETE TEST FILES
# ============================================

Write-Host "`n📋 Step 1: Deleting Test Files..." -ForegroundColor Yellow

$testFiles = @(
    # Python test files
    "test_all_v2_endpoints.py",
    "test_app_factory.py",
    "test_base_repository.py",
    "test_base_service.py",
    "test_community_repo.py",
    "test_core_extraction.py",
    "test_egg_combining.js",
    "test_final_completion.py",
    "test_friends_api.py",
    "test_friends_households_quick.py",
    "test_friends_query.py",
    "test_groq_integration.py",
    "test_integration.py",
    "test_local_api.py",
    "test_ollama.py",
    "test_phase1_community.py",
    "test_phase2_favorites.py",
    "test_phase3_profile.py",
    "test_phase4_pantry.py",
    "test_phase5_search.py",
    "test_phase6_system.py",
    "test_railway_api.py",
    "test_railway_deployment.py",
    "test_recipe_repository.py",
    "test_recipe_service.py",
    "test_share_debug.py",
    "test_social_backend.py",
    "test_spacy_endpoint.py",
    "test_spacy_metadata.py",
    "test_spacy_normalizer.py",
    "test_user_repository.py",
    "test_user_service.py",
    "test_v2_api.py",
    
    # PowerShell test files
    "test_complete_v2_api.ps1",
    "test_live_api.ps1",
    "test_meal_plan.ps1",
    "test_v2_complete.ps1",
    "test_v2_simple.ps1"
)

foreach ($file in $testFiles) {
    if (Test-Path $file) {
        Remove-Item $file -Force
        Write-Host "  ✅ Deleted: $file" -ForegroundColor Green
    }
}

Write-Host "  🎉 Test files deleted!" -ForegroundColor Green

# ============================================
# 2. ORGANIZE DOCUMENTATION
# ============================================

Write-Host "`n📋 Step 2: Organizing Documentation..." -ForegroundColor Yellow

# Create doc subdirectories if they don't exist
$docDirs = @(
    "docs/features",
    "docs/deployment",
    "docs/refactoring",
    "docs/guides",
    "docs/completed"
)

foreach ($dir in $docDirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

# Feature docs
$featureDocs = @(
    "FRIENDS_NOT_SHOWING_SOLVED.md",
    "FRIENDS_PORT_FIX.md",
    "FRIENDS_TOKEN_KEY_FIX.md",
    "GROCERY_LIST_LOADING_FIX.md",
    "GROCERY_LIST_MODERNIZATION.md",
    "GROCERY_LIST_OVERWRITE_FEATURE.md",
    "PREMIUM_FEATURE_PLAN.md",
    "SIDEBAR_COMMUNITY_UPDATES.md",
    "SOCIAL_FEATURES_INTEGRATION_COMPLETE.md",
    "REALTIME_COLLABORATION_GUIDE.md"
)

foreach ($file in $featureDocs) {
    if (Test-Path $file) {
        Move-Item $file "docs/features/$file" -Force
        Write-Host "  ✅ Moved to docs/features: $file" -ForegroundColor Green
    }
}

# Deployment docs
$deploymentDocs = @(
    "CORS_FIX_DEPLOYMENT.md",
    "DEPLOYMENT_STATUS_LIVE.md",
    "RAILWAY_DEPLOYMENT_STATUS.md",
    "READY_TO_DEPLOY.md"
)

foreach ($file in $deploymentDocs) {
    if (Test-Path $file) {
        Move-Item $file "docs/deployment/$file" -Force
        Write-Host "  ✅ Moved to docs/deployment: $file" -ForegroundColor Green
    }
}

# Refactoring docs
$refactoringDocs = @(
    "ARCHITECTURE_COMPARISON.md",
    "CLEANUP_PLAN.md",
    "FRONTEND_CLEANUP_NOTES.md",
    "MOBILE_FIRST_REFACTORING_PLAN.md",
    "REFACTORING_OVERVIEW.md",
    "REFACTORING_STRATEGY.md",
    "SAFE_REFACTORING_ROADMAP.md",
    "QUICK_START_REFACTORING.md",
    "RECIPE_SYSTEM_ARCHITECTURE_ANALYSIS.md",
    "ROOT_PYTHON_FILES_AUDIT.md"
)

foreach ($file in $refactoringDocs) {
    if (Test-Path $file) {
        Move-Item $file "docs/refactoring/$file" -Force
        Write-Host "  ✅ Moved to docs/refactoring: $file" -ForegroundColor Green
    }
}

# Guides
$guideDocs = @(
    "DATABASE_PERFORMANCE_GUIDE.md",
    "EMAIL_CAPTURE_GUIDE.md",
    "INTERNAL_TESTING_WELCOME_EMAIL.md",
    "PYTHON_ENVIRONMENT_GUIDE.md",
    "TESTING_GUIDE_FRIENDS_HOUSEHOLDS.md"
)

foreach ($file in $guideDocs) {
    if (Test-Path $file) {
        Move-Item $file "docs/guides/$file" -Force
        Write-Host "  ✅ Moved to docs/guides: $file" -ForegroundColor Green
    }
}

# Completed phase docs
$completedDocs = @(
    "PHASE_0_CHECKLIST.md",
    "PHASE_1_VIEW_EDIT_MODE_COMPLETE.md",
    "REVENUECAT_CLEANUP_COMPLETE.md",
    "REVENUECAT_CLEANUP_PLAN.md",
    "REVENUECAT_CLEANUP_SUMMARY.md"
)

foreach ($file in $completedDocs) {
    if (Test-Path $file) {
        Move-Item $file "docs/completed/$file" -Force
        Write-Host "  ✅ Moved to docs/completed: $file" -ForegroundColor Green
    }
}

Write-Host "  🎉 Documentation organized!" -ForegroundColor Green

# ============================================
# 3. ORGANIZE UTILITY SCRIPTS
# ============================================

Write-Host "`n📋 Step 3: Organizing Utility Scripts..." -ForegroundColor Yellow

# Create scripts subdirectory
if (-not (Test-Path "scripts/database")) {
    New-Item -ItemType Directory -Path "scripts/database" -Force | Out-Null
}
if (-not (Test-Path "scripts/setup")) {
    New-Item -ItemType Directory -Path "scripts/setup" -Force | Out-Null
}

# Database utility scripts
$dbScripts = @(
    "check_canonical_ingredients.py",
    "check_friends_tables.py",
    "check_meal_plan_formats.py",
    "check_railway_routes.py",
    "check_schema.py",
    "check_tables.py",
    "check_users.py",
    "check_user_11_friends.py",
    "cleanup_old_meal_plans.py",
    "debug_friends.py",
    "debug_grocery_insert.py",
    "find_regular_list.py",
    "find_user_with_recipes.py",
    "migrate_grocery_lists.py",
    "add_profile_fields.py"
)

foreach ($file in $dbScripts) {
    if (Test-Path $file) {
        Move-Item $file "scripts/database/$file" -Force
        Write-Host "  ✅ Moved to scripts/database: $file" -ForegroundColor Green
    }
}

# Setup/init scripts
$setupScripts = @(
    "init_community_tables.py",
    "init_favorites_table.py",
    "init_pantry_table.py",
    "init_recipe_imports_table.py",
    "init_social_db.py",
    "init_social_tables.py",
    "register_v2_routes.py"
)

foreach ($file in $setupScripts) {
    if (Test-Path $file) {
        Move-Item $file "scripts/setup/$file" -Force
        Write-Host "  ✅ Moved to scripts/setup: $file" -ForegroundColor Green
    }
}

# Specialized scripts (keep in root or move to scripts)
$specialScripts = @(
    "template_management.py",
    "template_recipe_system.py",
    "waitlist_api_endpoint.py"
)

foreach ($file in $specialScripts) {
    if (Test-Path $file) {
        Move-Item $file "scripts/$file" -Force
        Write-Host "  ✅ Moved to scripts: $file" -ForegroundColor Green
    }
}

Write-Host "  🎉 Utility scripts organized!" -ForegroundColor Green

# ============================================
# 4. SUMMARY
# ============================================

Write-Host "`n" -NoNewline
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host (" " * 50) -NoNewline
Write-Host "=" -ForegroundColor Cyan
Write-Host "🎊 CLEANUP COMPLETE!" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host (" " * 50) -NoNewline
Write-Host "=" -ForegroundColor Cyan

Write-Host "`n📊 Summary:" -ForegroundColor Cyan
Write-Host "  ✅ Deleted ~35 test files"
Write-Host "  ✅ Organized ~30 documentation files"
Write-Host "  ✅ Organized ~25 utility scripts"
Write-Host "  ✅ Root directory is now clean!"

Write-Host "`n📁 New Structure:" -ForegroundColor Cyan
Write-Host "  docs/features/     - Feature-specific docs"
Write-Host "  docs/deployment/   - Deployment docs"
Write-Host "  docs/refactoring/  - Refactoring docs"
Write-Host "  docs/guides/       - How-to guides"
Write-Host "  docs/completed/    - Completed phase docs"
Write-Host "  scripts/database/  - Database utilities"
Write-Host "  scripts/setup/     - Setup/init scripts"
Write-Host "  scripts/           - Other utility scripts"

Write-Host "`nRoot now contains only:" -ForegroundColor Cyan
Write-Host '  - Main app files'
Write-Host '  - Config files'
Write-Host '  - README and guides'
Write-Host '  - Key directories'

Write-Host ""
Write-Host "Ready to commit!" -ForegroundColor Green

