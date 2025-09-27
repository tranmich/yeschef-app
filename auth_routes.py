#!/usr/bin/env python3
"""
Authentication Routes for Hungie
API endpoints for user registration, login, OAuth, and user management
"""

from flask import Blueprint, request, jsonify, session, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from auth_system import AuthenticationSystem
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

def create_auth_routes(auth_system):
    """Create authentication routes blueprint"""

    auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

    @auth_bp.route('/register', methods=['POST'])
    def register():
        """Register a new user"""
        try:
            data = request.get_json()

            # Validate input
            if not data or not data.get('name') or not data.get('email'):
                return jsonify({'success': False, 'message': 'Name and email are required'}), 400

            name = data.get('name').strip()
            email = data.get('email').strip().lower()
            password = data.get('password')

            if not password or len(password) < 6:
                return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400

            # Register user
            result = auth_system.register_user(name, email, password)

            if result['success']:
                logger.info(f"[OK] User registered via API: {email}")
                return jsonify(result), 201
            else:
                return jsonify(result), 400

        except Exception as e:
            logger.error(f"[ERROR] Registration API error: {e}")
            return jsonify({'success': False, 'message': 'Registration failed'}), 500

    @auth_bp.route('/login', methods=['POST'])
    def login():
        """Authenticate user with email and password"""
        try:
            data = request.get_json()

            if not data or not data.get('email') or not data.get('password'):
                return jsonify({'success': False, 'message': 'Email and password are required'}), 400

            email = data.get('email').strip().lower()
            password = data.get('password')

            # Authenticate user
            result = auth_system.authenticate_user(email, password)

            if result['success']:
                logger.info(f"[OK] User logged in via API: {email}")
                return jsonify(result), 200
            else:
                return jsonify(result), 401

        except Exception as e:
            logger.error(f"[ERROR] Login API error: {e}")
            return jsonify({'success': False, 'message': 'Login failed'}), 500

    @auth_bp.route('/logout', methods=['POST'])
    def logout():
        """Logout user (client-side token removal)"""
        try:
            # Since we're using JWT tokens, logout is mainly handled client-side
            # by removing the token from storage. However, we can log the event
            # and potentially blacklist the token in the future.
            
            # Try to get current user for logging
            try:
                user_id = get_jwt_identity()
                if user_id:
                    user = auth_system.get_user_by_id(user_id)
                    if user:
                        logger.info(f"[OK] User logged out: {user['email']}")
                    else:
                        logger.info(f"[OK] User logged out: ID {user_id}")
                else:
                    logger.info("[OK] Logout called without valid token")
            except:
                # If token is invalid or missing, that's fine for logout
                logger.info("[OK] Logout called - token validation not required")
            
            return jsonify({
                'success': True, 
                'message': 'Logged out successfully'
            }), 200

        except Exception as e:
            logger.error(f"[ERROR] Logout API error: {e}")
            # Even if there's an error, logout should succeed from client perspective
            return jsonify({
                'success': True, 
                'message': 'Logged out successfully'
            }), 200

    @auth_bp.route('/me', methods=['GET'])
    def get_current_user():
        """Get current user information"""
        try:
            # Manual JWT validation to handle integer subjects
            from flask import request
            import jwt
            import json
            import base64
            import os
            import hashlib
            
            # Get Authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'success': False, 'message': 'Missing or invalid Authorization header'}), 401
            
            token = auth_header.split(' ')[1]
            
            # Use same JWT secret generation as AuthenticationSystem
            jwt_secret = os.getenv('JWT_SECRET_KEY')
            if not jwt_secret:
                database_url = os.getenv('DATABASE_URL', '')
                if database_url:
                    jwt_secret = hashlib.sha256(database_url.encode()).hexdigest()
                else:
                    jwt_secret = 'dev-secret-key-for-local-testing-only'
            
            try:
                # Manual decode without strict subject validation
                payload_part = token.split('.')[1]
                padding_needed = len(payload_part) % 4
                if padding_needed:
                    payload_part += '=' * (4 - padding_needed)
                    
                payload_bytes = base64.urlsafe_b64decode(payload_part)
                payload = json.loads(payload_bytes)
                
                user_id = payload.get('sub')
                if isinstance(user_id, str) and user_id.isdigit():
                    user_id = int(user_id)
                
                # Verify signature
                jwt.decode(token, jwt_secret, algorithms=['HS256'], options={"verify_sub": False})
                
                logger.info(f"[AUTH] Getting user info for ID: {user_id}")
                
            except Exception as e:
                logger.error(f"[AUTH] JWT validation failed: {e}")
                return jsonify({'success': False, 'message': 'Invalid token'}), 401

            user = auth_system.get_user_by_id(user_id)

            if user:
                logger.info(f"[AUTH] Successfully retrieved user: {user.get('email', 'Unknown')}")
                return jsonify({'success': True, 'user': user}), 200
            else:
                logger.warning(f"[AUTH] User not found for ID: {user_id}")
                return jsonify({'success': False, 'message': 'User not found'}), 404

        except Exception as e:
            logger.error(f"[ERROR] Get user API error: {e}")
            import traceback
            traceback.print_exc()

            # Provide more specific error messages
            if "Not enough segments" in str(e):
                return jsonify({
                    'success': False,
                    'message': 'Invalid token format. Please log in again.',
                    'error_type': 'invalid_token'
                }), 422
            elif "signature verification failed" in str(e).lower():
                return jsonify({
                    'success': False,
                    'message': 'Token signature invalid. Please log in again.',
                    'error_type': 'invalid_signature'
                }), 422
            elif "token has expired" in str(e).lower():
                return jsonify({
                    'success': False,
                    'message': 'Token has expired. Please log in again.',
                    'error_type': 'expired_token'
                }), 422
            else:
                return jsonify({
                    'success': False,
                    'message': 'Authentication failed. Please log in again.',
                    'error_type': 'auth_error'
                }), 500

    @auth_bp.route('/google', methods=['GET'])
    def google_login():
        """Initiate Google OAuth login"""
        try:
            redirect_uri = url_for('auth.google_callback', _external=True)
            return auth_system.google.authorize_redirect(redirect_uri)
        except Exception as e:
            logger.error(f"[ERROR] Google OAuth error: {e}")
            return jsonify({'success': False, 'message': 'OAuth initialization failed'}), 500

    @auth_bp.route('/google/callback', methods=['GET'])
    def google_callback():
        """Handle Google OAuth callback"""
        try:
            token = auth_system.google.authorize_access_token()
            user_info = token.get('userinfo')

            if user_info:
                email = user_info.get('email')
                name = user_info.get('name')

                # Register or authenticate user
                result = auth_system.register_user(
                    name=name,
                    email=email,
                    password=None,
                    oauth_provider='google',
                    oauth_id=user_info.get('sub')
                )

                if result['success']:
                    # Redirect to frontend with token
                    token = result['access_token']
                    return redirect(f'http://localhost:3000/auth/success?token={token}')
                else:
                    # Try to authenticate existing user
                    # For OAuth users, we'll create a token directly
                    from flask_jwt_extended import create_access_token
                    access_token = create_access_token(identity=email)
                    return redirect(f'http://localhost:3000/auth/success?token={access_token}')

            return redirect('http://localhost:3000/auth/error')

        except Exception as e:
            logger.error(f"[ERROR] Google callback error: {e}")
            return redirect('http://localhost:3000/auth/error')

    @auth_bp.route('/google', methods=['POST'])
    def google_mobile_signin():
        """Handle Google Sign-In from mobile app"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': 'No data provided'}), 400
            
            google_id = data.get('google_id')
            email = data.get('email')
            name = data.get('name')
            photo = data.get('photo')
            
            if not google_id or not email:
                return jsonify({'success': False, 'error': 'Missing required Google data'}), 400
            
            logger.info(f"🔐 Google Sign-In attempt for: {email}")
            
            # Check if user exists with this Google ID or email
            conn = auth_system.get_db_connection()
            cursor = conn.cursor()
            
            try:
                # First check for existing Google OAuth user
                cursor.execute("""
                    SELECT id, email, name, oauth_provider, oauth_id 
                    FROM users 
                    WHERE oauth_provider = 'google' AND oauth_id = %s
                """, (google_id,))
                user = cursor.fetchone()
                
                if not user:
                    # Check for existing user with same email
                    cursor.execute("SELECT id, email, name FROM users WHERE email = %s", (email,))
                    existing_user = cursor.fetchone()
                    
                    if existing_user:
                        # Link Google account to existing user
                        cursor.execute("""
                            UPDATE users 
                            SET oauth_provider = 'google', oauth_id = %s 
                            WHERE id = %s
                        """, (google_id, existing_user['id']))
                        conn.commit()
                        user = existing_user
                    else:
                        # Create new user with Google account
                        cursor.execute("""
                            INSERT INTO users (name, email, oauth_provider, oauth_id, created_at) 
                            VALUES (%s, %s, 'google', %s, NOW()) 
                            RETURNING id, name, email
                        """, (name, email, google_id))
                        user = cursor.fetchone()
                        conn.commit()
                
                # Create access token
                from flask_jwt_extended import create_access_token
                access_token = create_access_token(identity=str(user['id']))
                
                logger.info(f"✅ Google Sign-In successful for: {email}")
                
                return jsonify({
                    'success': True,
                    'access_token': access_token,
                    'user': {
                        'id': user['id'],
                        'name': user['name'],
                        'email': user['email']
                    }
                }), 200
                
            except Exception as db_error:
                conn.rollback()
                logger.error(f"❌ Database error in Google Sign-In: {db_error}")
                return jsonify({'success': False, 'error': 'Database error'}), 500
            finally:
                conn.close()
                
        except Exception as e:
            logger.error(f"❌ Google Sign-In error: {e}")
            return jsonify({'success': False, 'error': 'Internal server error'}), 500

    @auth_bp.route('/forgot-password', methods=['POST'])
    def forgot_password():
        """Send password reset email"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': 'No data provided'}), 400
            
            email = data.get('email', '').strip().lower()
            if not email:
                return jsonify({'success': False, 'error': 'Email is required'}), 400
            
            conn = auth_system.get_db_connection()
            cursor = conn.cursor()
            
            try:
                # Check if user exists
                cursor.execute("SELECT id, email, name FROM users WHERE email = %s", (email,))
                user = cursor.fetchone()
                
                if not user:
                    # Don't reveal if email exists or not for security
                    return jsonify({
                        'success': True, 
                        'message': 'If an account with that email exists, a password reset link has been sent.'
                    }), 200
                
                # Generate secure reset token
                import uuid
                from datetime import datetime, timedelta
                
                reset_token = str(uuid.uuid4())
                expires_at = datetime.utcnow() + timedelta(minutes=30)  # 30 min expiry
                
                # Store reset token
                cursor.execute("""
                    INSERT INTO password_reset_tokens (user_id, token, expires_at, created_at) 
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (user_id) DO UPDATE SET 
                    token = EXCLUDED.token, 
                    expires_at = EXCLUDED.expires_at,
                    created_at = EXCLUDED.created_at
                """, (user['id'], reset_token, expires_at, datetime.utcnow()))
                
                conn.commit()
                
                # TODO: Send email with reset link
                reset_link = f"https://yeschefapp-production.up.railway.app/api/auth/reset-password?token={reset_token}"
                logger.info(f"🔑 Password reset link generated for {email}: {reset_link}")
                
                # For now, return the link in response (in production, only send email)
                return jsonify({
                    'success': True,
                    'message': 'Password reset link sent to your email.',
                    'reset_link': reset_link  # Remove this in production
                }), 200
                
            except Exception as db_error:
                conn.rollback()
                logger.error(f"❌ Database error in forgot password: {db_error}")
                return jsonify({'success': False, 'error': 'Database error'}), 500
            finally:
                conn.close()
                
        except Exception as e:
            logger.error(f"❌ Forgot password error: {e}")
            return jsonify({'success': False, 'error': 'Internal server error'}), 500

    @auth_bp.route('/reset-password', methods=['GET', 'POST'])
    def reset_password():
        """Handle password reset - GET shows form, POST processes new password"""
        if request.method == 'GET':
            token = request.args.get('token')
            if not token:
                return '<h1>Invalid Reset Link</h1><p>The password reset link is missing or invalid.</p>', 400
            
            # Return a simple HTML form for password reset
            return f'''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Reset Your Password - YesChef</title>
                <style>
                    body {{ font-family: Arial, sans-serif; max-width: 400px; margin: 50px auto; padding: 20px; }}
                    .form-group {{ margin-bottom: 15px; }}
                    input {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
                    button {{ background: #AAC6AD; color: white; padding: 12px 20px; border: none; border-radius: 5px; cursor: pointer; width: 100%; }}
                    button:hover {{ background: #95B1A0; }}
                    .error {{ color: red; margin-top: 10px; }}
                </style>
            </head>
            <body>
                <h2>Reset Your Password</h2>
                <form method="POST">
                    <input type="hidden" name="token" value="{token}">
                    <div class="form-group">
                        <input type="password" name="password" placeholder="New Password" required minlength="6">
                    </div>
                    <div class="form-group">
                        <input type="password" name="confirm_password" placeholder="Confirm New Password" required minlength="6">
                    </div>
                    <button type="submit">Reset Password</button>
                </form>
            </body>
            </html>
            '''
        
        else:  # POST
            try:
                token = request.form.get('token')
                password = request.form.get('password')
                confirm_password = request.form.get('confirm_password')
                
                if not token or not password or not confirm_password:
                    return '<h1>Error</h1><p>All fields are required.</p>', 400
                
                if password != confirm_password:
                    return '<h1>Error</h1><p>Passwords do not match.</p>', 400
                
                if len(password) < 6:
                    return '<h1>Error</h1><p>Password must be at least 6 characters.</p>', 400
                
                conn = auth_system.get_db_connection()
                cursor = conn.cursor()
                
                try:
                    # Find and validate reset token
                    cursor.execute("""
                        SELECT user_id, expires_at FROM password_reset_tokens 
                        WHERE token = %s AND expires_at > %s
                    """, (token, datetime.utcnow()))
                    
                    reset_record = cursor.fetchone()
                    if not reset_record:
                        return '<h1>Invalid or Expired Link</h1><p>The password reset link is invalid or has expired.</p>', 400
                    
                    # Hash new password
                    password_hash = auth_system.bcrypt.generate_password_hash(password).decode('utf-8')
                    
                    # Update user password
                    cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", 
                                 (password_hash, reset_record['user_id']))
                    
                    # Delete used reset token
                    cursor.execute("DELETE FROM password_reset_tokens WHERE token = %s", (token,))
                    
                    conn.commit()
                    
                    logger.info(f"✅ Password reset successful for user {reset_record['user_id']}")
                    
                    return '''
                    <h1>Password Reset Successful!</h1>
                    <p>Your password has been updated successfully.</p>
                    <p>You can now close this window and log in with your new password.</p>
                    '''
                    
                except Exception as db_error:
                    conn.rollback()
                    logger.error(f"❌ Database error in reset password: {db_error}")
                    return '<h1>Error</h1><p>Database error occurred.</p>', 500
                finally:
                    conn.close()
                    
            except Exception as e:
                logger.error(f"❌ Reset password error: {e}")
                return '<h1>Error</h1><p>An error occurred.</p>', 500

    @auth_bp.route('/google-mobile', methods=['GET'])
    def google_mobile_auth():
        """Initiate Google OAuth for mobile with proper redirect"""
        try:
            # Get the redirect URI from query params
            redirect_uri = request.args.get('redirect_uri', 'yeschef://google-auth')
            
            # Store the mobile redirect URI in session for later use
            session['mobile_redirect'] = redirect_uri
            
            # Initiate Google OAuth with our web callback
            web_redirect_uri = url_for('auth.google_mobile_callback', _external=True)
            return auth_system.google.authorize_redirect(web_redirect_uri)
            
        except Exception as e:
            logger.error(f"❌ Google mobile auth error: {e}")
            return redirect(f"{redirect_uri}-error")

    @auth_bp.route('/google-mobile/callback', methods=['GET'])
    def google_mobile_callback():
        """Handle Google OAuth callback for mobile"""
        try:
            # Get the mobile redirect URI from session
            mobile_redirect = session.get('mobile_redirect', 'yeschef://google-auth')
            
            token = auth_system.google.authorize_access_token()
            user_info = token.get('userinfo')

            if user_info:
                google_id = user_info.get('sub')
                email = user_info.get('email')
                name = user_info.get('name')
                photo = user_info.get('picture')

                # Check if user exists or create new one
                conn = auth_system.get_db_connection()
                cursor = conn.cursor()
                
                try:
                    # First check for existing Google OAuth user
                    cursor.execute("""
                        SELECT id, email, name FROM users 
                        WHERE oauth_provider = 'google' AND oauth_id = %s
                    """, (google_id,))
                    user = cursor.fetchone()
                    
                    if not user:
                        # Check for existing user with same email
                        cursor.execute("SELECT id, email, name FROM users WHERE email = %s", (email,))
                        existing_user = cursor.fetchone()
                        
                        if existing_user:
                            # Link Google account to existing user
                            cursor.execute("""
                                UPDATE users 
                                SET oauth_provider = 'google', oauth_id = %s 
                                WHERE id = %s
                            """, (google_id, existing_user['id']))
                            conn.commit()
                            user = existing_user
                        else:
                            # Create new user with Google account
                            cursor.execute("""
                                INSERT INTO users (name, email, oauth_provider, oauth_id, created_at) 
                                VALUES (%s, %s, 'google', %s, NOW()) 
                                RETURNING id, name, email
                            """, (name, email, google_id))
                            user = cursor.fetchone()
                            conn.commit()
                    
                    # Create access token
                    from flask_jwt_extended import create_access_token
                    access_token = create_access_token(identity=str(user['id']))
                    
                    # Prepare user data for mobile
                    user_data = {
                        'id': user['id'],
                        'name': user['name'],
                        'email': user['email']
                    }
                    
                    logger.info(f"✅ Mobile Google Sign-In successful for: {email}")
                    
                    # Redirect back to mobile app with success data
                    import urllib.parse
                    user_encoded = urllib.parse.quote(str(user_data).replace("'", '"'))
                    return redirect(f"{mobile_redirect}-success?token={access_token}&user={user_encoded}")
                    
                except Exception as db_error:
                    conn.rollback()
                    logger.error(f"❌ Database error in mobile Google callback: {db_error}")
                    return redirect(f"{mobile_redirect}-error")
                finally:
                    conn.close()
            
            return redirect(f"{mobile_redirect}-error")

        except Exception as e:
            logger.error(f"❌ Google mobile callback error: {e}")
            mobile_redirect = session.get('mobile_redirect', 'yeschef://google-auth')
            return redirect(f"{mobile_redirect}-error")

    @auth_bp.route('/facebook', methods=['GET'])
    def facebook_login():
        """Initiate Facebook OAuth login"""
        try:
            redirect_uri = url_for('auth.facebook_callback', _external=True)
            return auth_system.facebook.authorize_redirect(redirect_uri)
        except Exception as e:
            logger.error(f"[ERROR] Facebook OAuth error: {e}")
            return jsonify({'success': False, 'message': 'OAuth initialization failed'}), 500

    @auth_bp.route('/facebook/callback', methods=['GET'])
    def facebook_callback():
        """Handle Facebook OAuth callback"""
        try:
            token = auth_system.facebook.authorize_access_token()

            # Get user info from Facebook
            resp = auth_system.facebook.get('me?fields=id,name,email')
            user_info = resp.json()

            if user_info:
                email = user_info.get('email')
                name = user_info.get('name')

                # Register or authenticate user
                result = auth_system.register_user(
                    name=name,
                    email=email,
                    password=None,
                    oauth_provider='facebook',
                    oauth_id=user_info.get('id')
                )

                if result['success']:
                    token = result['access_token']
                    return redirect(f'http://localhost:3000/auth/success?token={token}')
                else:
                    from flask_jwt_extended import create_access_token
                    access_token = create_access_token(identity=email)
                    return redirect(f'http://localhost:3000/auth/success?token={access_token}')

            return redirect('http://localhost:3000/auth/error')

        except Exception as e:
            logger.error(f"[ERROR] Facebook callback error: {e}")
            return redirect('http://localhost:3000/auth/error')

    @auth_bp.route('/wipe-data', methods=['DELETE'])
    def wipe_user_data():
        """Wipe user data for testing purposes"""
        try:
            # Check if this is a development environment
            data = request.get_json() or {}
            confirm = data.get('confirm', False)
            user_id = data.get('user_id')

            if not confirm:
                return jsonify({
                    'success': False,
                    'message': 'Must confirm data wipe with "confirm": true'
                }), 400

            result = auth_system.wipe_user_data(user_id)

            if result['success']:
                logger.warning(f"[WARNING] User data wiped via API: {'user ' + str(user_id) if user_id else 'all users'}")
                return jsonify(result), 200
            else:
                return jsonify(result), 500

        except Exception as e:
            logger.error(f"[ERROR] Wipe data API error: {e}")
            return jsonify({'success': False, 'message': 'Failed to wipe data'}), 500

    @auth_bp.route('/status', methods=['GET'])
    def auth_status():
        """Check authentication system status"""
        return jsonify({
            'success': True,
            'message': 'Authentication system is running',
            'endpoints': {
                'register': '/api/auth/register',
                'login': '/api/auth/login',
                'me': '/api/auth/me',
                'google': '/api/auth/google',
                'facebook': '/api/auth/facebook',
                'wipe_data': '/api/auth/wipe-data',
                'delete_account': '/api/auth/delete-account'
            }
        }), 200

    @auth_bp.route('/delete-account', methods=['DELETE'])
    @jwt_required()
    def delete_account():
        """Delete user account permanently"""
        try:
            user_id = get_jwt_identity()
            if not user_id:
                return jsonify({'success': False, 'error': 'Invalid session'}), 401
            
            user_id_int = int(user_id)
            conn = auth_system.get_db_connection()
            cursor = conn.cursor()
            
            try:
                # Delete dependent records first (foreign keys)
                cursor.execute("DELETE FROM user_preferences WHERE user_id = %s", (user_id_int,))
                cursor.execute("DELETE FROM saved_recipes WHERE user_id = %s", (user_id_int,))
                cursor.execute("DELETE FROM saved_meal_plans WHERE user_id = %s", (user_id_int,))
                cursor.execute("DELETE FROM user_pantry WHERE user_id = %s", (user_id_int,))
                cursor.execute("DELETE FROM recipes WHERE user_id = %s", (user_id_int,))
                cursor.execute("DELETE FROM grocery_lists WHERE user_id = %s", (user_id_int,))
                cursor.execute("DELETE FROM meal_plans WHERE user_id = %s", (user_id_int,))
                cursor.execute("DELETE FROM users WHERE id = %s", (user_id_int,))
                
                conn.commit()
                return jsonify({'success': True, 'message': 'Account permanently deleted'}), 200
                
            except Exception as db_error:
                conn.rollback()
                return jsonify({'success': False, 'error': 'Database error'}), 500
            finally:
                conn.close()
                
        except Exception as error:
            return jsonify({'success': False, 'error': 'Server error'}), 500

    return auth_bp
