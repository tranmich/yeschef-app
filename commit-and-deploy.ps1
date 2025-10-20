# 🚀 Git Commit and Deploy Script

Write-Host "🚀 Preparing to commit household collaboration features..." -ForegroundColor Green

# Navigate to project root
cd "D:\Mik\Downloads\Me Hungie"

Write-Host "`n📊 Checking git status..." -ForegroundColor Cyan
git status

Write-Host "`n➕ Adding new files..." -ForegroundColor Cyan

# New components for sharing
git add frontend/src/components/ShareResourceModal.js
git add frontend/src/components/ShareResourceModal.css

# API utilities
git add frontend/src/utils/householdAPI.js

# Modified components
git add frontend/src/components/GroceryManagerWorkspace.js
git add frontend/src/components/GroceryManagerWorkspace.css
git add frontend/src/components/MealPlannerView.js
git add frontend/src/components/MealPlannerView.css

# Mobile adapter fix
git add YesChefMobile/src/services/MobileMealPlanAdapter.js

# Documentation
git add frontend/PHASE_2_COMPLETE.md
git add frontend/PHASE_3_COMPLETE.md
git add frontend/PRODUCTION_DEPLOYMENT.md
git add YesChefMobile/MEAL_PLAN_ADAPTER_FIX.md

Write-Host "`n📝 Committing changes..." -ForegroundColor Cyan

git commit -m "feat: Add household collaboration and sharing features

✨ New Features:
- ShareResourceModal component for grocery lists and meal plans
- Household sharing with Editor/Viewer permissions
- Share buttons in grocery workspace and meal planner
- Cross-platform mobile compatibility

🔧 Technical Changes:
- Add householdAPI.js for household management
- Integrate ShareResourceModal with GroceryManagerWorkspace
- Integrate ShareResourceModal with MealPlannerView
- Fix MobileMealPlanAdapter for simplified format support
- Update button styling for consistency

📱 Mobile Compatibility:
- Fix meal plan data conversion (web → mobile)
- Support simplified recipe format at day level
- Maintain backward compatibility with traditional format

📚 Documentation:
- Phase 2 Complete: Grocery List Sharing
- Phase 3 Complete: Meal Plan Sharing
- Mobile adapter fix documentation
- Production deployment guide

🎯 Impact:
- Users can share grocery lists with households
- Users can share meal plans with households
- Choose Editor or Viewer permission levels
- Collaborate across web and mobile platforms
- Production-ready with proper environment config"

Write-Host "`n✅ Commit complete!" -ForegroundColor Green

Write-Host "`n🌐 Current git log (last commit):" -ForegroundColor Cyan
git log -1 --oneline

Write-Host "`n🚀 Ready to push!" -ForegroundColor Green
Write-Host "Run: git push origin main" -ForegroundColor Yellow

Write-Host "`n📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Push to GitHub: git push origin main" -ForegroundColor White
Write-Host "2. Vercel will auto-deploy (if connected)" -ForegroundColor White
Write-Host "3. Or manual deploy: cd frontend && vercel --prod" -ForegroundColor White
Write-Host "4. Verify at your Vercel URL" -ForegroundColor White

Write-Host "`n✨ All set for production! 🎉" -ForegroundColor Green
