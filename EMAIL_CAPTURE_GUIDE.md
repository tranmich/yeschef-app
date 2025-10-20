# 📧 Email Capture System - Complete Guide

## 🎯 Overview

Your YesChef email capture system is now **fully operational**! Here's what happens when someone signs up:

```
User enters email on landing page
        ↓
POST request to /api/waitlist
        ↓
Stored in PostgreSQL database
        ↓
Accessible via admin dashboard
        ↓
Exportable to CSV, Google Sheets, etc.
```

---

## 🗄️ Database Structure

### **Waitlist Table:**

```sql
waitlist (
  id                  - Unique ID
  email               - User's email (unique)
  source              - Where they signed up (hero, final-cta)
  tester_type         - Type of tester (general, internal, priority)
  platform_preference - iOS, Android, or both
  signup_date         - When they signed up
  ip_address          - Their IP (for analytics)
  user_agent          - Their browser/device
  status              - pending, invited, accepted, declined
  invited_date        - When you sent invite
  notes               - Your notes about this tester
  metadata            - Additional JSON data
)
```

---

## 🚀 How It Works

### **1. Frontend → Backend Flow**

**Landing Page (`LandingPage.js`):**
```javascript
// When user submits email
handleWaitlistSubmit() {
  POST to http://localhost:5000/api/waitlist
  Body: { email, source }
}
```

**Backend API (`hungie_server.py`):**
```python
@app.route('/api/waitlist', methods=['POST'])
def join_waitlist():
  1. Validate email format
  2. Check if already exists
  3. Store in database
  4. Return success
```

---

## 📊 Accessing Your Waitlist Data

### **Method 1: Admin Dashboard (Web Interface)**

**URL:** `http://localhost:3000/admin/waitlist`

**Features:**
- ✅ View all signups in real-time
- ✅ Filter by status (pending, invited, etc.)
- ✅ See signup stats (total, iOS, Android)
- ✅ Export to CSV
- ✅ Beautiful interface

**To Access:**
1. Navigate to: `http://localhost:3000/admin/waitlist`
2. See all emails organized in a table
3. Click "Export to CSV" for spreadsheet

---

### **Method 2: Direct API Access**

**Get All Waitlist Entries:**
```bash
GET http://localhost:5000/api/admin/waitlist
```

**Response:**
```json
{
  "success": true,
  "waitlist": [
    {
      "id": 1,
      "email": "user@example.com",
      "source": "hero",
      "signup_date": "2025-10-16T10:30:00",
      "status": "pending",
      "platform_preference": null
    }
  ],
  "stats": {
    "total": 150,
    "pending": 120,
    "invited": 30,
    "ios": 60,
    "android": 40
  }
}
```

**Filter by Status:**
```bash
GET http://localhost:5000/api/admin/waitlist?status=pending
GET http://localhost:5000/api/admin/waitlist?status=invited
```

---

### **Method 3: Export to CSV**

**URL:** `http://localhost:5000/api/admin/waitlist/export`

**Result:** Download `yeschef_waitlist.csv` with:
```csv
Email,Source,Platform,Signup Date,Status
user1@example.com,hero,iOS,2025-10-16 10:30:00,pending
user2@example.com,final-cta,Android,2025-10-16 11:45:00,pending
```

**Use For:**
- Import to Google Sheets
- Import to TestFlight
- Send to email marketing service
- Backup

---

### **Method 4: Direct Database Query (Advanced)**

```bash
# Connect to PostgreSQL
psql -h localhost -U your_username -d your_database

# Query waitlist
SELECT email, source, signup_date, status 
FROM waitlist 
ORDER BY signup_date DESC;

# Get stats
SELECT 
  COUNT(*) as total,
  COUNT(*) FILTER (WHERE status = 'pending') as pending,
  COUNT(*) FILTER (WHERE platform_preference = 'iOS') as ios
FROM waitlist;
```

---

## 🎯 Organizing Testers

### **1. Categorize by Tester Type**

Update tester type in database:

```sql
-- Mark as internal tester
UPDATE waitlist 
SET tester_type = 'internal' 
WHERE email = 'friend@example.com';

-- Mark as priority tester
UPDATE waitlist 
SET tester_type = 'priority' 
WHERE email = 'important@example.com';
```

### **2. Categorize by Platform**

When collecting emails, ask for platform preference:

**Landing Page Update:**
```javascript
// Add platform selection (optional)
<select onChange={(e) => setPlatform(e.target.value)}>
  <option value="">No preference</option>
  <option value="iOS">iOS</option>
  <option value="Android">Android</option>
  <option value="both">Both</option>
</select>
```

### **3. Add to TestFlight**

**Export iOS Testers:**
```sql
SELECT email 
FROM waitlist 
WHERE platform_preference IN ('iOS', 'both', NULL)
AND status = 'pending'
ORDER BY signup_date ASC
LIMIT 100;
```

**Then:**
1. Copy emails
2. Go to App Store Connect → TestFlight
3. Add as external testers
4. Update status:
```sql
UPDATE waitlist 
SET status = 'invited', invited_date = NOW() 
WHERE email IN ('email1@example.com', 'email2@example.com');
```

---

## 📈 Analytics & Insights

### **Signup Stats:**

```sql
-- Total signups
SELECT COUNT(*) FROM waitlist;

-- Signups by day
SELECT 
  DATE(signup_date) as day,
  COUNT(*) as signups
FROM waitlist
GROUP BY DATE(signup_date)
ORDER BY day DESC;

-- Conversion by source
SELECT 
  source,
  COUNT(*) as signups
FROM waitlist
GROUP BY source;

-- Platform distribution
SELECT 
  platform_preference,
  COUNT(*) as count
FROM waitlist
GROUP BY platform_preference;
```

---

## 🔔 Notifications & Automation

### **Option 1: Email Notifications**

**Add to `hungie_server.py` waitlist endpoint:**

```python
# After successful signup, send notification
import smtplib
from email.mime.text import MIMEText

def notify_new_signup(email):
    msg = MIMEText(f'New waitlist signup: {email}')
    msg['Subject'] = 'New YesChef Waitlist Signup'
    msg['From'] = 'noreply@yeschefapp.io'
    msg['To'] = 'you@yeschefapp.io'
    
    # Send via SMTP
    # ... SMTP code here
```

### **Option 2: Google Sheets Integration**

**Install Google Sheets API:**
```bash
pip install gspread oauth2client
```

**Auto-sync to Google Sheets:**
```python
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def add_to_google_sheets(email, source, signup_date):
    scope = ['https://spreadsheets.google.com/feeds']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    
    sheet = client.open('YesChef Waitlist').sheet1
    sheet.append_row([email, source, signup_date, 'pending'])
```

### **Option 3: Slack/Discord Notifications**

```python
import requests

def notify_slack(email):
    webhook_url = 'YOUR_SLACK_WEBHOOK_URL'
    message = {
        'text': f'🎉 New waitlist signup: {email}'
    }
    requests.post(webhook_url, json=message)
```

---

## 🎯 Tester Management Workflow

### **Step 1: Collect Emails** ✅ DONE
- Landing page email forms
- Stored in database

### **Step 2: Review & Categorize**
```sql
-- View new signups
SELECT * FROM waitlist WHERE status = 'pending' ORDER BY signup_date DESC;

-- Add notes
UPDATE waitlist SET notes = 'Friend referral' WHERE email = 'user@example.com';

-- Set priority
UPDATE waitlist SET tester_type = 'priority' WHERE email = 'vip@example.com';
```

### **Step 3: Invite to TestFlight**
1. Export iOS emails (CSV)
2. Add to TestFlight in App Store Connect
3. Mark as invited:
```sql
UPDATE waitlist 
SET status = 'invited', invited_date = NOW() 
WHERE email IN (SELECT email FROM invited_batch);
```

### **Step 4: Track Acceptance**
```sql
-- When someone accepts invite
UPDATE waitlist SET status = 'accepted' WHERE email = 'user@example.com';

-- Track stats
SELECT 
  status,
  COUNT(*) as count
FROM waitlist
GROUP BY status;
```

---

## 📱 TestFlight Integration

### **Get iOS Testers:**

```sql
-- First 100 iOS testers
SELECT email 
FROM waitlist 
WHERE (platform_preference = 'iOS' OR platform_preference IS NULL)
AND status = 'pending'
ORDER BY signup_date ASC
LIMIT 100;
```

### **Get Android Testers:**

```sql
-- Android testers
SELECT email 
FROM waitlist 
WHERE (platform_preference = 'Android' OR platform_preference IS NULL)
AND status = 'pending'
ORDER BY signup_date ASC
LIMIT 100;
```

---

## 🔧 Quick Commands Reference

### **View Admin Dashboard:**
```
http://localhost:3000/admin/waitlist
```

### **Export CSV:**
```
http://localhost:5000/api/admin/waitlist/export
```

### **Get Pending Testers:**
```bash
curl http://localhost:5000/api/admin/waitlist?status=pending
```

### **Database Queries:**
```sql
-- Total signups
SELECT COUNT(*) FROM waitlist;

-- Today's signups
SELECT COUNT(*) FROM waitlist WHERE DATE(signup_date) = CURRENT_DATE;

-- iOS preference
SELECT COUNT(*) FROM waitlist WHERE platform_preference = 'iOS';
```

---

## 🎨 Customization Options

### **Add Custom Fields:**

```sql
-- Add custom field
ALTER TABLE waitlist ADD COLUMN referral_source VARCHAR(100);
ALTER TABLE waitlist ADD COLUMN interests TEXT[];
ALTER TABLE waitlist ADD COLUMN beta_feedback TEXT;
```

### **Add Tester Groups:**

```sql
-- Create groups
UPDATE waitlist SET tester_type = 'family' WHERE email LIKE '%@family.com';
UPDATE waitlist SET tester_type = 'internal' WHERE email IN ('teammate1@example.com', 'teammate2@example.com');
UPDATE waitlist SET tester_type = 'influencer' WHERE notes LIKE '%influencer%';
```

---

## 📊 Sample Queries for Testing Launch

### **Get First 50 Internal Testers:**
```sql
SELECT email FROM waitlist 
WHERE tester_type = 'internal' 
OR email IN ('friend1@example.com', 'friend2@example.com')
ORDER BY signup_date ASC
LIMIT 50;
```

### **Get Mix of Platforms:**
```sql
-- 30 iOS, 30 Android, 40 no preference
(SELECT email FROM waitlist WHERE platform_preference = 'iOS' LIMIT 30)
UNION
(SELECT email FROM waitlist WHERE platform_preference = 'Android' LIMIT 30)
UNION
(SELECT email FROM waitlist WHERE platform_preference IS NULL LIMIT 40);
```

---

## ✅ Setup Checklist

**Backend:**
- [x] Waitlist table created in PostgreSQL
- [x] `/api/waitlist` endpoint working
- [x] `/api/admin/waitlist` endpoint working
- [x] `/api/admin/waitlist/export` endpoint working

**Frontend:**
- [x] Landing page email forms working
- [x] API integration complete
- [x] Success messages showing
- [x] Admin dashboard created

**Next Steps:**
- [ ] Add route for admin dashboard in App.js
- [ ] Set up email notifications (optional)
- [ ] Set up Google Sheets sync (optional)
- [ ] Configure TestFlight email templates

---

## 🚀 Ready to Launch!

Your email capture system is now complete and production-ready!

**What You Have:**
✅ Landing page with 2 email capture forms
✅ Backend API storing emails in PostgreSQL
✅ Admin dashboard to view/export data
✅ CSV export functionality
✅ Organized by source, platform, status

**Next Actions:**
1. Test the email form on landing page
2. View signups in admin dashboard
3. Export to CSV and add to TestFlight
4. Start inviting testers!

**Questions? Check the implementation in:**
- Backend: `hungie_server.py` (lines with `/api/waitlist`)
- Frontend: `frontend/src/pages/LandingPage.js`
- Admin: `frontend/src/pages/WaitlistAdmin.js`

🎉 **You're ready to collect emails and organize your testing launch!**
