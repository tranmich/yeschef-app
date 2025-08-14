# Railway Environment Variables Setup Guide

## Required Environment Variables:

### 1. OPENAI_API_KEY (CRITICAL)
- Value: Your OpenAI API key (starts with sk-...)
- This enables AI chat and smart substitutions
- Without this, users get "AI features disabled" message

### 2. ENVIRONMENT 
- Value: production
- This configures CORS and other production settings

### 3. DATABASE_URL (Optional)
- Value: hungie.db
- Railway will use the uploaded database file

## How to Add Environment Variables in Railway:

1. In your Railway project dashboard
2. Go to "Variables" tab
3. Click "New Variable"
4. Add each variable:
   - Name: OPENAI_API_KEY
   - Value: [your-openai-api-key]
   
   - Name: ENVIRONMENT  
   - Value: production

5. Click "Deploy" to restart with new variables

## After Deployment:

Your API will be available at: https://[your-project-name].railway.app

Test endpoints:
- https://[your-project-name].railway.app/
- https://[your-project-name].railway.app/api/recipes
- https://[your-project-name].railway.app/api/categories

## Next Steps:
1. Test all endpoints work in production
2. Update frontend to use production API URL
3. Deploy frontend to Vercel
4. Share with users for feedback!

## Troubleshooting:
- Check Railway logs if deployment fails
- Verify environment variables are set correctly
- Ensure all files uploaded properly to GitHub
