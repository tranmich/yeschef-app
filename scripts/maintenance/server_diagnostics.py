#!/usr/bin/env python3
"""
Server Diagnostic Tool for Hungie
Identifies crash sources and provides stability analysis
"""

import logging
import sys
import traceback
import signal
import threading
import time
from contextlib import contextmanager

# Enhanced logging setup
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('server_debug.log')
    ]
)
logger = logging.getLogger(__name__)

class ServerDiagnostics:
    def __init__(self):
        self.crash_count = 0
        self.startup_issues = []
        self.import_issues = []
        self.runtime_issues = []
        
    def log_startup_phase(self, phase_name):
        """Log each startup phase for crash isolation"""
        logger.info(f"[SEARCH] STARTUP PHASE: {phase_name}")
        
    def test_imports(self):
        """Test all critical imports individually"""
        logger.info("[TEST] Testing critical imports...")
        
        imports_to_test = [
            ("Flask core", "from flask import Flask, request, jsonify"),
            ("Flask CORS", "from flask_cors import CORS"),
            ("Authentication", "from auth_system import AuthenticationSystem"),
            ("Auth Routes", "from auth_routes import create_auth_routes"),
            ("Core Systems", "from core_systems.meal_planning_system import MealPlanningSystem"),
            ("Database", "import sqlite3"),
            ("OpenAI", "from openai import OpenAI"),
            ("Environment", "from dotenv import load_dotenv")
        ]
        
        for name, import_stmt in imports_to_test:
            try:
                exec(import_stmt)
                logger.info(f"[OK] {name}: OK")
            except Exception as e:
                logger.error(f"[ERROR] {name}: {e}")
                self.import_issues.append((name, str(e)))
    
    def test_flask_app_creation(self):
        """Test Flask app creation and configuration"""
        logger.info("[TEST] Testing Flask app creation...")
        
        try:
            from flask import Flask
            from flask_cors import CORS
            
            app = Flask(__name__)
            logger.info("[OK] Flask app created")
            
            CORS(app, resources={
                r"/api/*": {
                    "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
                    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                    "allow_headers": ["Content-Type", "Authorization"]
                }
            })
            logger.info("[OK] CORS configured")
            
            return app
            
        except Exception as e:
            logger.error(f"[ERROR] Flask app creation failed: {e}")
            self.startup_issues.append(("Flask App", str(e)))
            return None
    
    def test_auth_system(self, app):
        """Test authentication system initialization"""
        logger.info("[TEST] Testing authentication system...")
        
        if not app:
            logger.error("[ERROR] No Flask app provided")
            return None
            
        try:
            from auth_system import AuthenticationSystem
            from auth_routes import create_auth_routes
            
            auth_system = AuthenticationSystem(app)
            logger.info("[OK] Authentication system created")
            
            auth_routes = create_auth_routes(auth_system)
            logger.info("[OK] Authentication routes created")
            
            app.register_blueprint(auth_routes)
            logger.info("[OK] Authentication routes registered")
            
            return auth_system
            
        except Exception as e:
            logger.error(f"[ERROR] Authentication system failed: {e}")
            traceback.print_exc()
            self.startup_issues.append(("Authentication", str(e)))
            return None
    
    def test_database_connection(self):
        """Test database connectivity"""
        logger.info("[TEST] Testing database connection...")
        
        try:
            import sqlite3
            conn = sqlite3.connect('hungie.db')
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM recipes')
            count = cursor.fetchone()[0]
            conn.close()
            
            logger.info(f"[OK] Database connection OK - {count} recipes found")
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Database connection failed: {e}")
            self.startup_issues.append(("Database", str(e)))
            return False
    
    def test_server_startup(self, app):
        """Test if server can start without crashing"""
        logger.info("[TEST] Testing server startup...")
        
        if not app:
            logger.error("[ERROR] No Flask app to test")
            return False
            
        try:
            # Test with test client first
            with app.test_client() as client:
                response = client.get('/api/auth/status')
                logger.info(f"[OK] Test client OK - Status: {response.status_code}")
            
            # Create a quick server test
            @app.route('/diagnostic/ping')
            def ping():
                return {'status': 'alive', 'message': 'Server is running'}
            
            logger.info("[OK] Diagnostic route added")
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Server startup test failed: {e}")
            traceback.print_exc()
            self.startup_issues.append(("Server Test", str(e)))
            return False
    
    def run_full_diagnostic(self):
        """Run complete server diagnostic"""
        logger.info("[DIAGNOSTIC] Starting Server Diagnostic Suite")
        logger.info("=" * 60)
        
        # Phase 1: Import testing
        self.log_startup_phase("Import Testing")
        self.test_imports()
        
        # Phase 2: Flask app creation
        self.log_startup_phase("Flask App Creation")
        app = self.test_flask_app_creation()
        
        # Phase 3: Database testing
        self.log_startup_phase("Database Testing")
        self.test_database_connection()
        
        # Phase 4: Authentication system
        self.log_startup_phase("Authentication System")
        auth_system = self.test_auth_system(app)
        
        # Phase 5: Server startup test
        self.log_startup_phase("Server Startup Test")
        server_ok = self.test_server_startup(app)
        
        # Generate report
        self.generate_diagnostic_report()
        
        return app if server_ok else None
    
    def generate_diagnostic_report(self):
        """Generate diagnostic summary"""
        logger.info("[REPORT] DIAGNOSTIC REPORT")
        logger.info("=" * 60)
        
        if self.import_issues:
            logger.error("[ERROR] IMPORT ISSUES:")
            for name, error in self.import_issues:
                logger.error(f"   - {name}: {error}")
        else:
            logger.info("[OK] All imports successful")
        
        if self.startup_issues:
            logger.error("[ERROR] STARTUP ISSUES:")
            for name, error in self.startup_issues:
                logger.error(f"   - {name}: {error}")
        else:
            logger.info("[OK] All startup phases successful")
        
        logger.info("[CHECKLIST] RECOMMENDATIONS:")
        if self.import_issues or self.startup_issues:
            logger.info("   - Fix the issues above before deployment")
            logger.info("   - Test each component individually")
            logger.info("   - Add more error handling to problematic areas")
        else:
            logger.info("   - Server appears stable for deployment")
            logger.info("   - Consider production WSGI server (gunicorn)")
            logger.info("   - Add health check endpoints for monitoring")

def run_safe_server(app):
    """Run server with crash protection"""
    logger.info("[LAUNCH] Starting server with crash protection...")
    
    def signal_handler(signum, frame):
        logger.info("📡 Received shutdown signal")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        app.run(
            host="127.0.0.1",
            port=5000,
            debug=False,  # Disable debug to prevent reloader crashes
            use_reloader=False,
            threaded=True
        )
    except Exception as e:
        logger.error(f"[ERROR] Server crashed: {e}")
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    diagnostics = ServerDiagnostics()
    
    # Run diagnostic
    app = diagnostics.run_full_diagnostic()
    
    if app:
        logger.info("🎯 Diagnostic passed - Starting server...")
        success = run_safe_server(app)
        if not success:
            logger.error("[ERROR] Server failed to run")
            sys.exit(1)
    else:
        logger.error("[ERROR] Diagnostic failed - Server not started")
        sys.exit(1)
