# 🧹 RevenueCat Cleanup Plan

## 📋 Files to Remove

### **YesChefMobile Directory:**
1. `src/config/RevenueCatConfig.js` - Configuration file
2. `src/services/RevenueCatService.js` - Main service
3. `src/services/RevenueCatServiceMock.js` - Mock service
4. `src/utils/RevenueCatValidator.js` - Validation utility

### **Documentation:**
5. `docs/features/REVENUECAT_SETUP_GUIDE.md` - Setup guide

---

## 📝 Files to Update (Remove RevenueCat imports/references)

### **YesChefMobile:**
1. `src/contexts/PremiumContext.js` - Remove RevenueCat service import
2. `src/screens/PaywallScreen.js` - Remove RevenueCat service import
3. `src/screens/ProfileScreen.js` - Remove RevenueCat validator/service

### **Documentation:**
4. `docs/legal/PRIVACY_POLICY.md` - Remove RevenueCat references
5. `frontend/public/privacypolicy.html` - Remove RevenueCat references
6. `PROJECT_MASTER_GUIDE.md` - Remove RevenueCat references
7. `CLEANUP_PLAN.md` - Remove RevenueCat references
8. `docs/README.md` - Remove RevenueCat references

---

## ✅ Cleanup Strategy

### **Phase 1: Delete Files**
- Remove all 4 RevenueCat-specific files from YesChefMobile
- Remove setup guide from docs

### **Phase 2: Refactor Code**
- Update PremiumContext to use backend-based premium model
- Update PaywallScreen to prepare for Stripe/backend integration
- Update ProfileScreen to remove mock premium toggle

### **Phase 3: Update Documentation**
- Remove RevenueCat from privacy policy
- Update project guides
- Prepare for new premium model docs

---

## 🎯 Replacement Strategy

Instead of RevenueCat, we'll use:
- **Backend tier system** (PostgreSQL)
- **Stripe for payments** (web + mobile)
- **JWT tokens** for premium verification
- **Admin dashboard** for tier management

---

## 📦 Next Steps After Cleanup

1. ✅ Clean files removed
2. ✅ Code refactored
3. ✅ Documentation updated
4. ⏳ Build tier system (backend)
5. ⏳ Add Stripe integration
6. ⏳ Create premium UI components

---

**Ready to execute cleanup!**
