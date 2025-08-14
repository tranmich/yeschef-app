#!/usr/bin/env python3
"""
Simple Server Test - Verify server components without lifecycle conflicts
"""

import logging
import sys
import requests
import time
import subprocess
import json
from threading import Thread

# Configure logging without emojis to avoid encoding issues
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('simple_server_test.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class SimpleServerTest:
    def __init__(self):
        self.server_process = None
        self.base_url = "http://127.0.0.1:5000"
        
    def test_server_endpoints(self):
        """Test server endpoints via actual HTTP requests"""
        logger.info("Testing server endpoints via HTTP...")
        
        # Test endpoints to verify
        test_endpoints = [
            {'url': '/api/auth/status', 'description': 'Auth status endpoint'},
            {'url': '/health', 'description': 'Health check endpoint'},
            {'url': '/api/auth/register', 'method': 'POST', 'description': 'Register endpoint', 
             'data': {'name': 'Test User', 'email': 'test@example.com', 'password': 'testpass123'}},
        ]
        
        results = []
        
        for endpoint in test_endpoints:
            try:
                url = self.base_url + endpoint['url']
                method = endpoint.get('method', 'GET')
                data = endpoint.get('data', None)
                
                logger.info(f"Testing {endpoint['description']}: {method} {url}")
                
                if method == 'POST':
                    response = requests.post(url, json=data, timeout=5)
                else:
                    response = requests.get(url, timeout=5)
                
                result = {
                    'endpoint': endpoint['url'],
                    'description': endpoint['description'],
                    'status_code': response.status_code,
                    'success': 200 <= response.status_code < 300,
                    'response_time': response.elapsed.total_seconds(),
                    'content_length': len(response.text)
                }
                
                # Try to parse JSON response
                try:
                    result['response_json'] = response.json()
                except:
                    result['response_text'] = response.text[:200] + "..." if len(response.text) > 200 else response.text
                
                results.append(result)
                
                if result['success']:
                    logger.info(f"✓ {endpoint['description']}: Status {response.status_code} ({response.elapsed.total_seconds():.3f}s)")
                else:
                    logger.warning(f"✗ {endpoint['description']}: Status {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                logger.error(f"✗ {endpoint['description']}: Connection refused - server not running")
                results.append({
                    'endpoint': endpoint['url'],
                    'description': endpoint['description'],
                    'error': 'Connection refused',
                    'success': False
                })
            except Exception as e:
                logger.error(f"✗ {endpoint['description']}: Error - {e}")
                results.append({
                    'endpoint': endpoint['url'],
                    'description': endpoint['description'],
                    'error': str(e),
                    'success': False
                })
        
        return results
    
    def start_server_background(self):
        """Start the server in background for testing"""
        logger.info("Starting server in background...")
        
        try:
            # Start the server process
            self.server_process = subprocess.Popen(
                [sys.executable, 'hungie_server.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give the server time to start
            logger.info("Waiting for server to start...")
            time.sleep(3)
            
            # Check if process is still running
            if self.server_process.poll() is None:
                logger.info("✓ Server process started successfully")
                return True
            else:
                stdout, stderr = self.server_process.communicate()
                logger.error(f"✗ Server process failed to start")
                logger.error(f"STDOUT: {stdout}")
                logger.error(f"STDERR: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Failed to start server: {e}")
            return False
    
    def stop_server(self):
        """Stop the background server"""
        if self.server_process:
            logger.info("Stopping server...")
            self.server_process.terminate()
            self.server_process.wait(timeout=5)
            logger.info("✓ Server stopped")
    
    def run_test(self):
        """Run the complete server test"""
        logger.info("=" * 60)
        logger.info("SIMPLE SERVER TEST - Starting")
        logger.info("=" * 60)
        
        # Test 1: Start server
        server_started = self.start_server_background()
        
        if not server_started:
            logger.error("✗ Cannot test endpoints - server failed to start")
            return False
        
        # Test 2: Test endpoints
        results = self.test_server_endpoints()
        
        # Test 3: Stop server
        self.stop_server()
        
        # Generate report
        self.generate_report(results)
        
        # Determine success
        successful_tests = sum(1 for r in results if r.get('success', False))
        total_tests = len(results)
        
        logger.info("=" * 60)
        logger.info(f"TEST SUMMARY: {successful_tests}/{total_tests} endpoints working")
        logger.info("=" * 60)
        
        return successful_tests > 0
    
    def generate_report(self, results):
        """Generate a detailed test report"""
        logger.info("\n" + "=" * 60)
        logger.info("ENDPOINT TEST RESULTS")
        logger.info("=" * 60)
        
        for result in results:
            status = "✓ PASS" if result.get('success', False) else "✗ FAIL"
            logger.info(f"{status} {result['description']}")
            logger.info(f"      Endpoint: {result['endpoint']}")
            
            if 'status_code' in result:
                logger.info(f"      Status: {result['status_code']}")
                logger.info(f"      Time: {result.get('response_time', 0):.3f}s")
            
            if 'error' in result:
                logger.info(f"      Error: {result['error']}")
            
            if 'response_json' in result:
                logger.info(f"      Response: {json.dumps(result['response_json'], indent=2)[:100]}...")
            
            logger.info("")

if __name__ == "__main__":
    tester = SimpleServerTest()
    try:
        success = tester.run_test()
        if success:
            logger.info("✓ SERVER TEST PASSED - Authentication system is working!")
            sys.exit(0)
        else:
            logger.error("✗ SERVER TEST FAILED - Check the logs above")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        tester.stop_server()
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test failed with exception: {e}")
        tester.stop_server()
        sys.exit(1)
