# Environment Management Guide

## The Problem We Solved (August 18, 2025)
`.env.local` was overriding `.env` with production URLs, causing frontend to call production server instead of local backend during development.

## Environment File Hierarchy in React
React loads environment files in this order (highest to lowest priority):
1. `.env.local` - ALWAYS loaded (except in test environment)
2. `.env.development` - loaded when NODE_ENV=development  
3. `.env.production` - loaded when NODE_ENV=production
4. `.env` - always loaded (lowest priority)

## Best Practices

### 1. Use .env for Shared Defaults
```bash
# .env - Base configuration for all environments
REACT_APP_API_URL=http://127.0.0.1:5000
REACT_APP_ENVIRONMENT=development
DISABLE_ESLINT_PLUGIN=true
CI=false
```

### 2. Use .env.local for Personal Overrides ONLY
```bash
# .env.local - Personal developer settings (like API keys, debug flags)
# WARNING: This file overrides everything else!
REACT_APP_DEBUG_MODE=true
# REACT_APP_API_URL=http://127.0.0.1:5000  # Don't duplicate common settings!
```

### 3. Use .env.development/.env.production for Environment-Specific Settings
```bash
# .env.development - Development-only settings
REACT_APP_API_URL=http://127.0.0.1:5000
REACT_APP_LOG_LEVEL=debug

# .env.production - Production-only settings  
REACT_APP_API_URL=https://yeschefapp-production.up.railway.app
REACT_APP_LOG_LEVEL=error
```

## Debugging Commands

### Check Current Environment Variables
```bash
# In React app console:
console.log('API URL:', process.env.REACT_APP_API_URL);
console.log('Environment:', process.env.REACT_APP_ENVIRONMENT);
console.log('Node ENV:', process.env.NODE_ENV);
```

### List All Environment Files
```bash
# Windows PowerShell
Get-ChildItem frontend\.env*

# Expected output:
# .env
# .env.local (only if you need personal overrides)
```

### Check Which File is Taking Precedence
Add this to your React component temporarily:
```javascript
useEffect(() => {
  console.log('=== Environment Debug ===');
  console.log('API URL:', process.env.REACT_APP_API_URL);
  console.log('Environment:', process.env.REACT_APP_ENVIRONMENT);
  console.log('All REACT_APP vars:', Object.keys(process.env).filter(key => key.startsWith('REACT_APP')));
}, []);
```

## Recommended Setup

### For Most Developers:
- Keep only `.env` with local development settings
- Delete `.env.local` unless you need personal overrides
- Use `.env.development` and `.env.production` for environment-specific configs

### For Production Deployment:
- Use environment variables in hosting platform (Railway, Vercel, etc.)
- Never commit `.env.local` to git (already in .gitignore)

## Quick Fix Commands

### Reset to Clean State:
```bash
# Remove potentially problematic files
cd frontend
Remove-Item .env.local -ErrorAction SilentlyContinue
Remove-Item .env.development -ErrorAction SilentlyContinue
Remove-Item .env.production -ErrorAction SilentlyContinue

# Keep only .env with local development settings
# Restart development server
npm start
```

### Verify Environment:
```bash
# Test API connectivity
curl "http://127.0.0.1:5000/api/health"

# Should return local backend response, not production
```

## Warning Signs
- Frontend making calls to production URL during development
- Environment variables not updating despite changes to .env
- Different behavior between developers on same codebase
- Mysterious "it works on my machine" issues

## The Golden Rule
**If you're debugging environment issues, check `.env.local` first!**
