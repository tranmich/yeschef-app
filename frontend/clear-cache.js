// Clear browser cache script
// Run this in browser console (F12) to clear all cached data

console.log('🧹 Clearing YesChef cache and storage...');

// Clear localStorage
localStorage.clear();
console.log('✅ localStorage cleared');

// Clear sessionStorage
sessionStorage.clear();
console.log('✅ sessionStorage cleared');

// Clear service workers (if any)
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.getRegistrations().then(registrations => {
    registrations.forEach(registration => registration.unregister());
    console.log('✅ Service workers cleared');
  });
}

// Clear cache storage
if ('caches' in window) {
  caches.keys().then(names => {
    names.forEach(name => caches.delete(name));
    console.log('✅ Cache storage cleared');
  });
}

console.log('✨ All clear! Now refresh the page (Ctrl+Shift+R)');
