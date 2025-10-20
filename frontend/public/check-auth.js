/**
 * Authentication Status Checker
 * Run this in browser console to check authentication status
 */

// Check if token exists
const token = localStorage.getItem('token');
console.log('🔑 Token exists:', !!token);
if (token) {
  console.log('Token preview:', token.substring(0, 50) + '...');
}

// Check if user data exists
const userData = localStorage.getItem('user');
console.log('👤 User data exists:', !!userData);
if (userData) {
  try {
    const user = JSON.parse(userData);
    console.log('User:', user);
  } catch (e) {
    console.error('Failed to parse user data:', e);
  }
}

// Test API call
async function testFriendsAPI() {
  try {
    const response = await fetch('http://localhost:5000/api/friends/list', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    console.log('📡 Friends API Response:', response.status);
    
    if (response.ok) {
      const data = await response.json();
      console.log('Friends data:', data);
    } else {
      const error = await response.json();
      console.error('API Error:', error);
    }
  } catch (error) {
    console.error('Network error:', error);
  }
}

console.log('\n📋 Run testFriendsAPI() to check friends endpoint');
console.log('💡 If you see errors, you need to login at /login');

// Export function for manual testing
window.testFriendsAPI = testFriendsAPI;