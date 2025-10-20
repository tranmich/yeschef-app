/**
 * Quick Browser Console Test for Friends API
 * 
 * Copy and paste this into your browser console (F12) while on http://localhost:3000
 * to test if the friends API is now working correctly
 */

console.log('🧪 Testing Friends API Fix...\n');

// Check 1: Verify token exists with correct key
const authToken = localStorage.getItem('authToken');
const wrongToken = localStorage.getItem('token');

console.log('1️⃣ Token Check:');
console.log('   ✅ authToken exists:', !!authToken);
console.log('   ❌ token exists:', !!wrongToken);
console.log('   Token preview:', authToken ? authToken.substring(0, 30) + '...' : 'NONE');

// Check 2: Test API endpoint directly
console.log('\n2️⃣ Testing /api/friends/list endpoint...');

fetch('http://127.0.0.1:5000/api/friends/list', {
  headers: {
    'Authorization': `Bearer ${authToken}`,
    'Content-Type': 'application/json'
  }
})
.then(response => {
  console.log('   Status:', response.status);
  return response.json();
})
.then(data => {
  console.log('   ✅ Success!');
  console.log('   Friends count:', data.count || 0);
  console.log('   Friends data:', data.friends);
  
  if (data.friends && data.friends.length > 0) {
    console.log('\n🎉 FRIENDS API WORKING!');
    console.log('   Found friends:');
    data.friends.forEach(friend => {
      console.log(`     - ${friend.name} (${friend.email})`);
    });
  } else {
    console.log('\n⚠️ API works but no friends returned');
    console.log('   Check if friendships exist in database');
  }
})
.catch(error => {
  console.error('   ❌ Error:', error);
  console.log('\n💡 Troubleshooting:');
  console.log('   1. Make sure backend is running on port 5000');
  console.log('   2. Check if you\'re logged in');
  console.log('   3. Verify token exists in localStorage');
});

console.log('\n📋 Instructions:');
console.log('   1. If you see "FRIENDS API WORKING!" → Refresh the page!');
console.log('   2. If you see errors → Check the troubleshooting steps above');
console.log('   3. Navigate to Friends tab to see your friends');
