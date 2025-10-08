# 🚀 RevenueCat Setup Guide for YesChef

## 📱 Step 1: App Store Setup

### Google Play Console
1. **Upload your APK/AAB** (even for internal testing)
2. **Note your Package Name**: `com.yeschef.app` (or whatever you choose)
3. **Create In-App Products**:
   ```
   Product ID: yeschef_premium_monthly
   Product ID: yeschef_premium_yearly
   ```
4. **Set up subscriptions** with pricing

### Apple App Store Connect
1. **Create app listing**
2. **Note your Bundle ID**: `com.yeschef.YesChefMobile` (or whatever you choose)
3. **Create Auto-Renewable Subscriptions**:
   ```
   Product ID: yeschef_premium_monthly
   Product ID: yeschef_premium_yearly
   ```

## 🔧 Step 2: RevenueCat Setup

### Create Project
1. Go to [RevenueCat Dashboard](https://app.revenuecat.com)
2. **Create new project**: "YesChef"
3. **Add your apps**:
   - iOS: Bundle ID from App Store Connect
   - Android: Package Name from Google Play Console

### Configure Products
1. **Products Tab** → Add products:
   ```
   yeschef_premium_monthly (Monthly Subscription)
   yeschef_premium_yearly (Annual Subscription)
   ```

2. **Entitlements Tab** → Create:
   ```
   premium (Your main premium entitlement)
   ```

3. **Offerings Tab** → Configure:
   ```
   default (Your default offering with both products)
   ```

### Get API Keys
1. **API Keys Tab** → Copy:
   ```
   iOS API Key: appl_xxxxxxxxxxxxx
   Android API Key: goog_xxxxxxxxxxxxx
   ```

## ⚙️ Step 3: Update YesChef Code

Update `src/config/RevenueCatConfig.js`:

```javascript
export const REVENUECAT_CONFIG = {
  API_KEYS: {
    ios: 'appl_your_real_ios_key_here',
    android: 'goog_your_real_android_key_here',
  },

  PRODUCTS: {
    monthly: 'yeschef_premium_monthly',     // ✅ Match your store products
    yearly: 'yeschef_premium_yearly',       // ✅ Match your store products
  },

  APP_CONFIG: {
    bundleId: {
      ios: 'com.yeschef.YesChefMobile',     // ✅ Your actual Bundle ID
      android: 'com.yeschef.app',           // ✅ Your actual Package Name
    },
  },
};
```

## 🧪 Step 4: Testing

### Sandbox Testing
1. **Create sandbox users** in App Store Connect / Google Play Console
2. **Test purchases** with sandbox accounts
3. **Verify subscription status** in RevenueCat dashboard

### Test Flows
- [ ] Purchase monthly subscription
- [ ] Purchase yearly subscription  
- [ ] Restore purchases
- [ ] Cancel subscription
- [ ] Verify feature access

## 📋 Current Status

✅ **RevenueCat Integration**: Complete and ready  
⏳ **API Keys**: Waiting for store setup  
⏳ **Product IDs**: Waiting for store setup  
✅ **UI Components**: PaywallScreen, PremiumStatus ready  
✅ **Feature Gating**: Recipe sharing example implemented  

## 🔄 When Ready

1. Replace placeholder values in `RevenueCatConfig.js`
2. Test with sandbox accounts
3. Gate additional features as needed
4. Launch to production!

## 💡 Pro Tips

- **Start with internal testing** to get package names established
- **Use sandbox accounts** for testing before going live
- **RevenueCat provides great debugging tools** in their dashboard
- **Test restore purchases thoroughly** - very important for user experience

---

**You're on the right track! Set up your app stores first, then we'll configure the real RevenueCat integration.** 🎯