# 🐛 Railway Deployment Troubleshooting

## **Common Issues & Solutions**

---

## **Issue #1: "No module named spacy"**

### **Error:**
```
RUN python -m spacy download en_core_web_md
/usr/local/bin/python: No module named spacy
ERROR: failed to build: exit code: 1
```

### **Root Cause:**
spaCy was missing from `requirements.txt`, but Dockerfile tried to download the spaCy model before installing requirements.

### **Solution:**
✅ **FIXED** - Added `spacy==3.7.5` to requirements.txt

### **Build Order:**
```dockerfile
# 1. Install Python dependencies (includes spaCy)
RUN pip install --no-cache-dir -r requirements.txt

# 2. Download spaCy model (spaCy now available!)
RUN python -m spacy download en_core_web_md

# 3. Copy application code
COPY . .
```

### **Prevention:**
Always ensure all Python packages are in `requirements.txt` before trying to use them in Dockerfile RUN commands.

---

## **Issue #2: Out of Memory During Build**

### **Error:**
```
Building... OOMKilled
Process killed
```

### **Root Cause:**
Not enough memory allocated during build phase.

### **Solution:**
1. Go to Railway dashboard
2. Click your service
3. Go to "Settings" → "Resources"
4. Increase memory to **8 GB**

### **Why 8 GB?**
- Ollama: ~2 GB
- Llama model: ~2 GB  
- spaCy model: ~500 MB
- Build tools: ~1 GB
- Working space: ~2.5 GB

---

## **Issue #3: Ollama Not Starting**

### **Error in logs:**
```
ollama: command not found
```

### **Root Cause:**
Ollama installation failed or PATH not set.

### **Solution:**
Check Dockerfile has:
```dockerfile
# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh
```

### **Verify:**
```bash
railway run bash
which ollama
ollama --version
```

---

## **Issue #4: Model Download Timeout**

### **Error:**
```
Downloading llama3.2:3b... timeout
```

### **Root Cause:**
Model download (2 GB) taking too long, Railway times out.

### **Solution:**
The startup script handles this with retries:
```bash
ollama pull llama3.2:3b || \
  (sleep 5 && ollama pull llama3.2:3b)
```

If still failing:
1. Check Railway logs
2. Wait and retry
3. Network may be slow - try deploying again

---

## **Issue #5: Flask App Won't Start**

### **Error:**
```
Address already in use
Port 5000 is busy
```

### **Root Cause:**
Port conflict or service not starting properly.

### **Solution:**
1. Check `Dockerfile` exposes port 5000:
   ```dockerfile
   EXPOSE 5000 11434
   ```

2. Check Flask runs on correct port:
   ```python
   app.run(host='0.0.0.0', port=5000)
   ```

3. Railway automatically assigns PORT, update code:
   ```python
   port = int(os.environ.get('PORT', 5000))
   app.run(host='0.0.0.0', port=port)
   ```

---

## **Issue #6: Database Connection Failed**

### **Error:**
```
psycopg2.OperationalError: could not connect to server
```

### **Root Cause:**
`DATABASE_URL` environment variable not set or PostgreSQL not added.

### **Solution:**
1. Add PostgreSQL in Railway:
   - Click "New" → "Database" → "PostgreSQL"
   
2. Railway auto-sets `DATABASE_URL`
   
3. Verify in Settings → Variables:
   ```
   DATABASE_URL=postgresql://...
   ```

---

## **Issue #7: Environment Variables Missing**

### **Error:**
```
KeyError: 'SECRET_KEY'
Config variable not found
```

### **Root Cause:**
Required environment variables not set in Railway.

### **Solution:**
Set these in Railway → Settings → Variables:
```bash
FLASK_APP=hungie_server.py
FLASK_ENV=production
SECRET_KEY=<your-secret-key>
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
PYTHONUNBUFFERED=1
```

---

## **Issue #8: Long Build Times**

### **Symptom:**
First deployment taking 20+ minutes.

### **This is NORMAL!** ✅

**Why so long?**
- Docker image build: 5 min
- Install dependencies: 3 min
- Download Ollama: 2 min
- Download Llama model: 10 min (2 GB!)
- Start services: 1 min

**Subsequent builds:** 3-5 minutes (model cached)

---

## **Issue #9: Health Check Failing**

### **Error:**
```
Service unhealthy
Health check timeout
```

### **Root Cause:**
Services not ready when health check runs.

### **Solution:**
Add health check delay in `railway.json`:
```json
{
  "healthcheckPath": "/api/health",
  "healthcheckTimeout": 300
}
```

Or create health endpoint that checks all services:
```python
@app.route('/api/health')
def health_check():
    return {
        'status': 'healthy',
        'services': {
            'database': check_db(),
            'spacy': check_spacy(),
            'ollama': check_ollama()
        }
    }
```

---

## **Issue #10: spaCy Model Not Found**

### **Error:**
```
OSError: [E050] Can't find model 'en_core_web_md'
```

### **Root Cause:**
Model download failed during build.

### **Solution:**
1. Check build logs for spaCy download
2. Manually download in running container:
   ```bash
   railway run bash
   python -m spacy download en_core_web_md
   ```
3. Restart service

### **Permanent Fix:**
Ensure Dockerfile has:
```dockerfile
RUN python -m spacy download en_core_web_md
```

---

## **🔍 DEBUGGING TIPS:**

### **1. Check Build Logs**
Railway Dashboard → Service → Deployments → Click deployment → View logs

### **2. Check Runtime Logs**
Railway Dashboard → Service → Logs tab

### **3. Access Container**
```bash
railway run bash
```

Then check:
```bash
# Check Python version
python --version

# Check installed packages
pip list | grep spacy
pip list | grep flask

# Check Ollama
ollama --version
ollama list

# Check processes
ps aux
```

### **4. Test Locally First**
```bash
# Build locally
docker build -f Dockerfile.railway -t yeschef-test .

# Run locally
docker run -p 5000:5000 yeschef-test
```

### **5. Environment Variable Debug**
Add to your code:
```python
import os
print("Environment variables:")
for key, value in os.environ.items():
    if 'SECRET' not in key:  # Don't print secrets!
        print(f"{key}={value}")
```

---

## **📞 GET HELP:**

### **Railway Support:**
- Discord: https://discord.gg/railway
- Docs: https://docs.railway.app
- Status: https://status.railway.app

### **Check Logs Order:**
1. **Build logs** - Did build succeed?
2. **Deploy logs** - Did deployment start?
3. **Runtime logs** - Is app running?
4. **Metrics** - Resource usage OK?

---

## **✅ PREVENTION CHECKLIST:**

Before deploying:
- [ ] All dependencies in requirements.txt
- [ ] Dockerfile tested locally
- [ ] Environment variables documented
- [ ] Health check endpoint working
- [ ] Database migrations ready
- [ ] Resource requirements calculated
- [ ] Backup/rollback plan ready

---

**Last Updated:** October 9, 2025  
**Status:** Issue #1 fixed, ready for deployment! 🚀
