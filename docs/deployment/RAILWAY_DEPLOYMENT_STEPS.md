# 🚀 Railway Deployment - Step by Step
**Deploy YesChef Backend with Ollama LLM Support**

---

## **📋 PREREQUISITES:**

✅ GitHub repository pushed with latest code  
✅ Railway account (https://railway.app)  
✅ Railway CLI installed (optional)  

---

## **🎯 DEPLOYMENT STEPS:**

### **Step 1: Access Railway Dashboard**

1. Go to: https://railway.app
2. Click **"Login"** (use GitHub)
3. Click **"New Project"**

---

### **Step 2: Create New Project**

1. Click **"Deploy from GitHub repo"**
2. Select: **`tranmich/yeschef-app`**
3. Railway will automatically detect:
   - ✅ `railway.json` (configuration)
   - ✅ `Dockerfile.railway` (build instructions)
   - ✅ `requirements.txt` (dependencies)

---

### **Step 3: Configure Environment**

Railway will ask you to set up the service. Click on the service and add these **Environment Variables**:

#### **Required Variables:**

```bash
# Flask Configuration
FLASK_APP=hungie_server.py
FLASK_ENV=production
SECRET_KEY=<generate-a-random-secret-key>

# Database (Railway will auto-provide these if you add PostgreSQL)
DATABASE_URL=<railway-will-provide>

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b

# Python
PYTHONUNBUFFERED=1
```

#### **How to Generate SECRET_KEY:**

In Python terminal:
```python
import secrets
print(secrets.token_hex(32))
```

Copy the output and use it for `SECRET_KEY`.

---

### **Step 4: Add PostgreSQL Database**

1. In your Railway project, click **"New"**
2. Select **"Database"**
3. Choose **"PostgreSQL"**
4. Railway will automatically:
   - Create the database
   - Set `DATABASE_URL` environment variable
   - Link it to your service

---

### **Step 5: Configure Build Settings**

Railway should automatically detect these from `railway.json`, but verify:

**Build Configuration:**
- **Builder:** Docker
- **Dockerfile Path:** `Dockerfile.railway`
- **Build Command:** (automatic)

**Deploy Configuration:**
- **Start Command:** `python hungie_server.py`
- **Port:** 5000 (automatic from Dockerfile)

---

### **Step 6: Resource Settings**

**CRITICAL:** Make sure your service has enough resources!

1. Click on your service
2. Go to **"Settings"**
3. Scroll to **"Resources"**
4. Set:
   - **Memory:** 8 GB (Hobby plan supports this!)
   - **CPU:** 2 vCPU (minimum)

**Why 8 GB?**
- Flask app: ~500 MB
- spaCy: ~500 MB
- Ollama: ~2 GB
- Llama 3.2 3B model: ~2 GB
- Working memory: ~3 GB
- **Total:** ~8 GB

---

### **Step 7: Deploy!**

1. Click **"Deploy"**
2. Railway will:
   - ⏳ Clone your repo
   - ⏳ Build Docker image (10-15 minutes first time)
   - ⏳ Download Ollama
   - ⏳ Download Llama 3.2 3B model (~2 GB)
   - ⏳ Start services
   - ✅ Deploy!

**First deployment will take 15-20 minutes** due to model download.

---

### **Step 8: Monitor Deployment**

Watch the deployment logs:

**Expected logs:**
```
✅ Building Docker image...
✅ Installing Python dependencies...
✅ Installing Ollama...
✅ Downloading llama3.2:3b model...
   ⏳ Pulling model... (this takes time!)
✅ Model downloaded successfully
✅ Starting Ollama service...
✅ Starting Flask app...
🚀 Running on http://0.0.0.0:5000
✅ Deployment successful!
```

**If you see errors:**
- Check logs for specific error
- Verify environment variables
- Check memory allocation (needs 8 GB!)

---

### **Step 9: Get Your Deployment URL**

1. Once deployed, Railway provides a public URL
2. Click **"Settings"** → **"Domains"**
3. You'll see something like:
   ```
   https://yeschef-production-abc123.up.railway.app
   ```
4. **Save this URL!** You'll need it for mobile app.

---

### **Step 10: Test Deployment**

Test the health endpoint:

```bash
curl https://your-app.up.railway.app/api/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "services": {
    "database": "connected",
    "spacy": "loaded",
    "ollama": "ready"
  }
}
```

---

### **Step 11: Test Ollama**

Test the Ollama integration:

```bash
curl -X POST https://your-app.up.railway.app/api/ollama/test \
  -H "Content-Type: application/json" \
  -d '{"question": "Should chicken thighs and chicken broth combine?"}'
```

**Expected response:**
```json
{
  "success": true,
  "response": "No, they should not be combined. Chicken thighs are raw meat, while chicken broth is a liquid ingredient.",
  "processing_time": 1.2
}
```

---

### **Step 12: Update Mobile App**

Update the mobile app to use the new Railway URL:

**File:** `YesChefMobile/src/services/YesChefAPI.js`

```javascript
class YesChefAPI {
  constructor() {
    // 🔧 PRODUCTION: Use Railway URL
    this.baseURL = 'https://your-app.up.railway.app';
    
    // 🔧 DEVELOPMENT: Use local
    // this.baseURL = 'http://192.168.1.72:5000';
    
    this.token = null;
    this.user = null;
    this.debugMode = true;
  }
  // ...
}
```

---

## **🎛️ OPTIONAL: Railway CLI Deployment**

For faster deployments in the future:

### **Install Railway CLI:**

```powershell
npm install -g railway
```

### **Login:**

```powershell
railway login
```

### **Link to Project:**

```powershell
cd "D:\Mik\Downloads\Me Hungie"
railway link
```

### **Deploy with One Command:**

```powershell
railway up
```

---

## **📊 MONITORING:**

### **Check Logs:**

**Via Dashboard:**
1. Go to Railway dashboard
2. Click your service
3. Click **"Logs"** tab
4. See real-time logs

**Via CLI:**

```powershell
railway logs
```

### **Check Metrics:**

**Via Dashboard:**
1. Click your service
2. Click **"Metrics"** tab
3. See:
   - Memory usage
   - CPU usage
   - Network traffic
   - Request count

---

## **💰 COST TRACKING:**

**Railway Hobby Plan:**
- **Base:** $5/month
- **Usage:** Pay for what you use
- **Resources:** Up to 8 GB RAM, 8 vCPU

**Expected Monthly Cost:**
- **Low traffic** (< 1000 users): $5-10/month
- **Medium traffic** (1000-5000 users): $10-20/month
- **High traffic** (5000+ users): $20-30/month

**Monitor in Dashboard:**
- Click **"Usage"** tab
- See current month's usage
- Set budget alerts

---

## **🔧 TROUBLESHOOTING:**

### **Issue: Build Failed**

**Check:**
1. Dockerfile.railway exists
2. Requirements.txt is valid
3. Python version is correct (3.11+)

**Solution:**
```bash
# Test build locally
docker build -f Dockerfile.railway -t yeschef-test .
```

---

### **Issue: Out of Memory**

**Symptoms:**
- Deployment crashes
- Service restarts
- "OOM" in logs

**Solution:**
1. Verify you have 8 GB allocated
2. Check if model downloaded (takes 2 GB)
3. Consider upgrading to Pro plan if needed

---

### **Issue: Ollama Not Responding**

**Check logs for:**
```
✅ Starting Ollama service...
```

**If missing:**
1. Check Dockerfile.railway has Ollama installation
2. Verify OLLAMA_HOST environment variable
3. Check Ollama process is running:
   ```bash
   railway run bash
   ps aux | grep ollama
   ```

---

### **Issue: Model Not Found**

**Symptoms:**
- "model not found" errors
- Ollama returns 404

**Solution:**
1. Check build logs for model download
2. Verify OLLAMA_MODEL environment variable
3. Manually pull model:
   ```bash
   railway run bash
   ollama pull llama3.2:3b
   ```

---

### **Issue: Slow Response Times**

**Check:**
1. Memory usage (should be < 80%)
2. CPU usage (should be < 80%)
3. Network latency
4. Database connection

**Solution:**
- Enable caching for LLM responses
- Optimize database queries
- Consider upgrading resources

---

## **🎯 POST-DEPLOYMENT CHECKLIST:**

- [ ] Service deployed successfully
- [ ] Health endpoint responding
- [ ] Ollama endpoint responding
- [ ] Database connected
- [ ] Environment variables set
- [ ] Domain/URL configured
- [ ] Mobile app updated with new URL
- [ ] Test grocery list generation
- [ ] Monitor logs for errors
- [ ] Set up budget alerts
- [ ] Document deployment URL

---

## **📚 NEXT STEPS:**

1. ✅ Deploy to Railway
2. 🧪 Test all endpoints
3. 📱 Update mobile app URL
4. 🎨 Test grocery combining with LLM
5. 📊 Monitor performance
6. 🔄 Set up CI/CD (optional)

---

## **🆘 NEED HELP?**

**Railway Support:**
- Discord: https://discord.gg/railway
- Docs: https://docs.railway.app

**Your Deployment:**
- Check logs first
- Verify environment variables
- Test locally with Docker
- Check Railway status page

---

**Ready to deploy!** 🚀

**Current Status:** Code pushed to GitHub, ready for Railway!
