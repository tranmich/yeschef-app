#!/usr/bin/env node

/**
 * Environment Debug Script
 * Run this to see which environment files are being loaded and in what order
 * Usage: node debug-env.js
 */

const fs = require('fs');
const path = require('path');

console.log('=== React Environment Debug ===\n');

const envFiles = [
  '.env.local',
  '.env.development',
  '.env.production',
  '.env'
];

console.log('Environment files found (in load order):');
envFiles.forEach((file, index) => {
  const filePath = path.join(__dirname, file);
  if (fs.existsSync(filePath)) {
    const content = fs.readFileSync(filePath, 'utf8');
    console.log(`${index + 1}. ✅ ${file} (${content.split('\n').length} lines)`);

    // Extract REACT_APP variables
    const reactAppVars = content
      .split('\n')
      .filter(line => line.startsWith('REACT_APP_') && !line.startsWith('#'))
      .map(line => '    ' + line);

    if (reactAppVars.length > 0) {
      console.log('   React App Variables:');
      reactAppVars.forEach(v => console.log(v));
    }
    console.log('');
  } else {
    console.log(`${index + 1}. ❌ ${file} (not found)`);
  }
});

console.log('Current NODE_ENV:', process.env.NODE_ENV || 'undefined');
console.log('\n=== Recommendations ===');

if (fs.existsSync('.env.local')) {
  console.log('⚠️  WARNING: .env.local found - this overrides all other env files!');
  console.log('   Consider moving personal settings to .env.development instead.');
}

if (!fs.existsSync('.env')) {
  console.log('❌ Missing .env file - create one with default development settings');
}

console.log('\n=== Quick Commands ===');
console.log('Remove .env.local:     Remove-Item .env.local');
console.log('Test local backend:    curl "http://127.0.0.1:5000/api/health"');
console.log('Restart dev server:    npm start');
