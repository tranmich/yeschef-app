# 🚀 Railway Deployment - Quick Reference Card

## **📋 Environment Variables (Copy & Paste)**

```bash
FLASK_APP=hungie_server.py
FLASK_ENV=production
SECRET_KEY=172ef4e0df6789ddce0b8b5cd49729c90074aebb468b2d5320025d4c895a3400
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
PYTHONUNBUFFERED=1
```

---

## **🎛️ Resource Settings**

| Setting | Value |
|---------|-------|
| Memory | 8 GB |
| CPU | 2 vCPU |

---

## **✅ Deployment Checklist**

- [ ] Go to https://railway.app
- [ ] Login with GitHub
- [ ] Click "New Project"
- [ ] Select "Deploy from GitHub repo"
- [ ] Choose: `tranmich/yeschef-app`
- [ ] Add PostgreSQL database
- [ ] Set environment variables (see above)
- [ ] Set memory to 8 GB
- [ ] Click "Deploy"
- [ ] Wait 15-20 minutes for first deploy
- [ ] Test health endpoint: `/api/health`
- [ ] Save deployment URL
- [ ] Update mobile app with new URL

---

## **🧪 Test Commands**

### **Health Check:**
```bash
curl https://YOUR-APP.up.railway.app/api/health
```

### **Ollama Test:**
```bash
curl -X POST https://YOUR-APP.up.railway.app/api/ollama/test \
  -H "Content-Type: application/json" \
  -d '{"question": "Should chicken thighs and chicken broth combine?"}'
```

### **spaCy Test:**
```bash
curl -X POST https://YOUR-APP.up.railway.app/api/grocery/extract-metadata \
  -H "Content-Type: application/json" \
  -d '{"items": [{"id": "1", "name": "2 chicken breasts"}]}'
```

---

## **📱 Mobile App Update**

**File:** `YesChefMobile/src/services/YesChefAPI.js`

```javascript
class YesChefAPI {
  constructor() {
    // 🔧 UPDATE THIS with your Railway URL:
    this.baseURL = 'https://YOUR-APP.up.railway.app';
    // ...
  }
}
```

---

## **💰 Expected Costs**

| Usage Level | Monthly Cost |
|-------------|--------------|
| Low (< 1K users) | $5-10 |
| Medium (1K-5K users) | $10-20 |
| High (5K+ users) | $20-30 |

---

## **⏱️ Expected Timings**

| Event | Time |
|-------|------|
| First deployment | 15-20 min |
| Subsequent deploys | 3-5 min |
| Model download | 5-10 min |
| Health check response | < 1 sec |
| Ollama response | 1-3 sec |

---

## **🆘 Common Issues**

### **Build Failed:**
- Check Dockerfile.railway exists
- Verify requirements.txt
- Check Python version (3.11+)

### **Out of Memory:**
- Verify 8 GB allocated
- Check model downloaded
- Monitor usage tab

### **Ollama Not Working:**
- Check OLLAMA_HOST variable
- Verify model downloaded
- Check logs for "Starting Ollama"

---

## **📊 Monitoring**

**Dashboard:** https://railway.app/project/YOUR-PROJECT

**Tabs to watch:**
- **Logs** - Real-time application logs
- **Metrics** - Memory, CPU, network
- **Usage** - Cost tracking
- **Settings** - Environment variables

---

## **🔗 Important Links**

- **Railway Dashboard:** https://railway.app
- **Railway Docs:** https://docs.railway.app
- **Railway Discord:** https://discord.gg/railway
- **GitHub Repo:** https://github.com/tranmich/yeschef-app

---

## **📝 Notes**

- ✅ Code is pushed to GitHub
- ✅ All configurations ready
- ✅ Documentation complete
- ⏳ Ready to deploy!

---

**Last Updated:** October 9, 2025  
**Status:** Ready for deployment! 🚀
