"""
YesChef Waitlist API Endpoint
Add this to hungie_server.py to handle waitlist signups from landing page
"""

from flask import jsonify, request
from datetime import datetime
import sqlite3
import re

# Add this route to hungie_server.py

@app.route('/api/waitlist', methods=['POST', 'OPTIONS'])
def waitlist_signup():
    """
    Handle waitlist email signups from landing page
    Stores email and timestamp for beta invites
    """
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        
        # Validate email format
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not email or not re.match(email_regex, email):
            return jsonify({
                'success': False,
                'error': 'Invalid email address'
            }), 400
        
        # Connect to database
        conn = sqlite3.connect('hungie.db')
        cursor = conn.cursor()
        
        # Create waitlist table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS waitlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                signup_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                invited BOOLEAN DEFAULT 0,
                invite_sent_date TIMESTAMP NULL,
                status TEXT DEFAULT 'pending',
                source TEXT DEFAULT 'landing_page',
                notes TEXT NULL
            )
        ''')
        
        # Check if email already exists
        cursor.execute('SELECT email, status FROM waitlist WHERE email = ?', (email,))
        existing = cursor.fetchone()
        
        if existing:
            status = existing[1]
            if status == 'invited':
                message = 'You\'re already on the list! Check your email for your invite.'
            elif status == 'active':
                message = 'You already have access! Please check your email for login details.'
            else:
                message = 'You\'re already on the waitlist! We\'ll reach out soon.'
            
            return jsonify({
                'success': True,
                'message': message,
                'already_exists': True
            })
        
        # Add to waitlist
        cursor.execute('''
            INSERT INTO waitlist (email, signup_date, source)
            VALUES (?, ?, ?)
        ''', (email, datetime.now(), 'landing_page'))
        
        conn.commit()
        conn.close()
        
        # TODO: Send confirmation email
        # send_waitlist_confirmation_email(email)
        
        # Log for analytics
        print(f"[WAITLIST] New signup: {email}")
        
        return jsonify({
            'success': True,
            'message': 'Successfully added to waitlist!',
            'email': email
        })
        
    except sqlite3.IntegrityError:
        return jsonify({
            'success': False,
            'error': 'Email already registered'
        }), 400
        
    except Exception as e:
        print(f"[ERROR] Waitlist signup failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to process signup. Please try again.'
        }), 500


@app.route('/api/waitlist/stats', methods=['GET'])
def waitlist_stats():
    """
    Get waitlist statistics (admin only)
    Returns count of signups and conversion metrics
    """
    # TODO: Add admin authentication check
    
    try:
        conn = sqlite3.connect('hungie.db')
        cursor = conn.cursor()
        
        # Get total signups
        cursor.execute('SELECT COUNT(*) FROM waitlist')
        total = cursor.fetchone()[0]
        
        # Get signups by status
        cursor.execute('''
            SELECT status, COUNT(*) 
            FROM waitlist 
            GROUP BY status
        ''')
        by_status = dict(cursor.fetchall())
        
        # Get recent signups (last 7 days)
        cursor.execute('''
            SELECT COUNT(*) 
            FROM waitlist 
            WHERE signup_date >= datetime('now', '-7 days')
        ''')
        recent = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'total_signups': total,
            'by_status': by_status,
            'recent_7_days': recent
        })
        
    except Exception as e:
        print(f"[ERROR] Failed to get waitlist stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve stats'
        }), 500


@app.route('/api/waitlist/export', methods=['GET'])
def export_waitlist():
    """
    Export waitlist emails (admin only)
    Returns CSV of all emails for sending invites
    """
    # TODO: Add admin authentication check
    
    try:
        conn = sqlite3.connect('hungie.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT email, signup_date, status, invited 
            FROM waitlist 
            ORDER BY signup_date ASC
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        # Format as CSV
        csv_data = "email,signup_date,status,invited\n"
        for row in results:
            csv_data += f"{row[0]},{row[1]},{row[2]},{row[3]}\n"
        
        return csv_data, 200, {
            'Content-Type': 'text/csv',
            'Content-Disposition': 'attachment; filename=yeschef_waitlist.csv'
        }
        
    except Exception as e:
        print(f"[ERROR] Failed to export waitlist: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to export'
        }), 500


# Optional: Email confirmation function (integrate with your email service)
def send_waitlist_confirmation_email(email):
    """
    Send confirmation email to new waitlist signups
    TODO: Integrate with SendGrid, Mailgun, or AWS SES
    """
    subject = "You're on the YesChef Waitlist! 🎉"
    
    body = f"""
    Hi there!
    
    Thanks for joining the YesChef beta waitlist. We're excited to have you!
    
    YesChef helps you preserve family recipes and organize your kitchen life. 
    From any source, in seconds.
    
    We're currently in invite-only beta testing with close family and friends. 
    You'll receive an invite link via email within the next few weeks.
    
    In the meantime:
    - Follow us for updates (add social links)
    - Reply to this email with any questions
    
    Everything in its place,
    The YesChef Team
    
    ---
    Not interested anymore? No problem, just ignore this email.
    """
    
    # TODO: Implement actual email sending
    # Example with SendGrid:
    # from sendgrid import SendGridAPIClient
    # from sendgrid.helpers.mail import Mail
    # 
    # message = Mail(
    #     from_email='hello@yeschef.app',
    #     to_emails=email,
    #     subject=subject,
    #     plain_text_content=body
    # )
    # sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    # response = sg.send(message)
    
    print(f"[EMAIL] Confirmation sent to {email}")
    return True


"""
USAGE INSTRUCTIONS:

1. Add these routes to hungie_server.py (after your other routes)

2. Update CORS settings to allow frontend domain:
   from flask_cors import CORS
   CORS(app, origins=["https://yourdomain.com", "http://localhost:3000"])

3. Update frontend LandingPage.js to use real API:
   In handleWaitlistSubmit, replace the TODO with:
   
   const response = await fetch(`${process.env.REACT_APP_API_URL}/api/waitlist`, {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({ email })
   });
   const data = await response.json();

4. Test locally:
   - Start backend: python hungie_server.py
   - Start frontend: npm start
   - Submit email on landing page
   - Check hungie.db for new entry in waitlist table

5. View waitlist:
   GET /api/waitlist/stats - See signup metrics
   GET /api/waitlist/export - Download CSV of emails

6. Send invites:
   - Export CSV
   - Send personalized invite emails with TestFlight/Play Store links
   - Update status to 'invited' in database
"""
