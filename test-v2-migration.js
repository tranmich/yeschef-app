#!/usr/bin/env node
/**
 * V2 Recipe API Migration Test Suite
 * 
 * This script tests all v2 recipe endpoints to verify the migration was successful.
 * Run this AFTER starting both backend and frontend servers.
 * 
 * Usage:
 *   node test-v2-migration.js
 * 
 * Prerequisites:
 *   - Backend running on http://localhost:5000
 *   - Valid user account with auth token
 *   - npm install axios dotenv
 */

const axios = require('axios');
const fs = require('fs');
const path = require('path');

// Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
const TEST_USER_EMAIL = process.env.TEST_USER_EMAIL || 'test1@gmail.com';
const TEST_USER_PASSWORD = process.env.TEST_USER_PASSWORD || 'testtest';

// ANSI color codes for terminal output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m'
};

// Test results tracking
let totalTests = 0;
let passedTests = 0;
let failedTests = 0;
const testResults = [];

// Utility functions
function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function logSection(title) {
  console.log('\n' + '='.repeat(80));
  log(`  ${title}`, 'cyan');
  console.log('='.repeat(80) + '\n');
}

function logTest(testName, status, details = '') {
  totalTests++;
  const icon = status === 'PASS' ? '✓' : '✗';
  const color = status === 'PASS' ? 'green' : 'red';
  
  if (status === 'PASS') {
    passedTests++;
  } else {
    failedTests++;
  }
  
  log(`${icon} ${testName}`, color);
  if (details) {
    log(`  ${details}`, 'yellow');
  }
  
  testResults.push({ testName, status, details });
}

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Authentication
let authToken = null;
let userId = null;

async function authenticate() {
  logSection('🔐 AUTHENTICATION TEST');
  
  try {
    log('Attempting to log in...', 'blue');
    const response = await axios.post(`${API_BASE_URL}/api/v2/auth/login`, {
      email: TEST_USER_EMAIL,
      password: TEST_USER_PASSWORD
    });
    
    if (response.data.success && response.data.data.token) {
      authToken = response.data.data.token;
      userId = response.data.data.user.id;
      logTest('Authentication', 'PASS', `User ID: ${userId}`);
      return true;
    } else {
      logTest('Authentication', 'FAIL', 'No token in response');
      return false;
    }
  } catch (error) {
    logTest('Authentication', 'FAIL', error.message);
    log('\n⚠️  Make sure you have a test user account created!', 'yellow');
    log(`   Email: ${TEST_USER_EMAIL}`, 'yellow');
    log(`   Password: ${TEST_USER_PASSWORD}`, 'yellow');
    return false;
  }
}

// Test helper to make authenticated requests
async function apiRequest(method, endpoint, data = null, isFormData = false) {
  const config = {
    method,
    url: `${API_BASE_URL}${endpoint}`,
    headers: {
      'Authorization': `Bearer ${authToken}`
    }
  };
  
  if (data) {
    if (isFormData) {
      config.data = data;
      config.headers['Content-Type'] = 'multipart/form-data';
    } else {
      config.data = data;
      config.headers['Content-Type'] = 'application/json';
    }
  }
  
  return axios(config);
}

// Test 1: Get User Recipes (v2)
async function testGetUserRecipes() {
  logSection('📚 TEST 1: GET USER RECIPES (V2)');
  
  try {
    log(`GET /api/v2/recipes/user/${userId}`, 'blue');
    const response = await apiRequest('GET', `/api/v2/recipes/user/${userId}`);
    
    if (response.data.success) {
      const recipes = response.data.data?.items || response.data.data || [];
      const pagination = response.data.data?.pagination;
      
      logTest('Get User Recipes', 'PASS', `Found ${recipes.length} recipes`);
      
      if (pagination) {
        log(`  Pagination: Page ${pagination.page}/${pagination.total_pages}, Total: ${pagination.total}`, 'blue');
      }
      
      return recipes;
    } else {
      logTest('Get User Recipes', 'FAIL', response.data.error);
      return [];
    }
  } catch (error) {
    logTest('Get User Recipes', 'FAIL', error.response?.data?.error || error.message);
    return [];
  }
}

// Test 2: Get User Recipes with Stats (THE STAR ENDPOINT)
async function testGetUserRecipesWithStats() {
  logSection('⭐ TEST 2: GET USER RECIPES WITH STATS (THE STAR!)');
  
  try {
    log(`GET /api/v2/recipes/user/${userId}/stats`, 'blue');
    const response = await apiRequest('GET', `/api/v2/recipes/user/${userId}/stats`);
    
    if (response.data.success) {
      const stats = response.data.data?.stats;
      const recipes = response.data.data?.recipes || [];
      
      logTest('Get User Recipes with Stats', 'PASS', `${recipes.length} recipes with stats`);
      
      if (stats) {
        log(`  Stats:`, 'blue');
        log(`    Total Recipes: ${stats.total_recipes}`, 'blue');
        log(`    Categories: ${stats.categories?.join(', ') || 'None'}`, 'blue');
        log(`    Recent: ${stats.recent_recipes?.length || 0}`, 'blue');
      }
      
      return recipes;
    } else {
      logTest('Get User Recipes with Stats', 'FAIL', response.data.error);
      return [];
    }
  } catch (error) {
    logTest('Get User Recipes with Stats', 'FAIL', error.response?.data?.error || error.message);
    return [];
  }
}

// Test 3: Import Recipe from URL
async function testImportFromURL() {
  logSection('🌐 TEST 3: IMPORT RECIPE FROM URL (V2)');
  
  const testURL = 'https://www.allrecipes.com/recipe/23600/worlds-best-lasagna/';
  
  try {
    log(`POST /api/v2/recipes/import/url`, 'blue');
    log(`  URL: ${testURL}`, 'blue');
    
    const response = await apiRequest('POST', '/api/v2/recipes/import/url', {
      url: testURL,
      user_id: userId
    });
    
    if (response.data.success) {
      const recipe = response.data.data?.recipe || response.data.recipe_data;
      const recipeId = response.data.data?.recipe_id || response.data.recipe_id;
      
      logTest('Import from URL', 'PASS', `Recipe: "${recipe?.title}" (ID: ${recipeId})`);
      log(`  Confidence: ${(response.data.data?.confidence || response.data.confidence || 0) * 100}%`, 'blue');
      
      return recipeId;
    } else {
      logTest('Import from URL', 'FAIL', response.data.error);
      return null;
    }
  } catch (error) {
    console.error('URL Import Error:', error.response?.data || error.message);
    logTest('Import from URL', 'FAIL', error.response?.data?.error || error.message);
    return null;
  }
}

// Test 4: Import Recipe from Text
async function testImportFromText() {
  logSection('📝 TEST 4: IMPORT RECIPE FROM TEXT (V2)');
  
  const sampleRecipe = `Chocolate Chip Cookies

Ingredients:
- 2 1/4 cups all-purpose flour
- 1 tsp baking soda
- 1 tsp salt
- 1 cup butter, softened
- 3/4 cup sugar
- 2 eggs
- 2 cups chocolate chips

Instructions:
1. Preheat oven to 375°F
2. Mix dry ingredients
3. Cream butter and sugar
4. Add eggs
5. Combine wet and dry ingredients
6. Fold in chocolate chips
7. Bake for 9-11 minutes`;
  
  try {
    log(`POST /api/v2/recipes/import/text`, 'blue');
    
    const response = await apiRequest('POST', '/api/v2/recipes/import/text', {
      text: sampleRecipe,
      user_id: userId
    });
    
    if (response.data.success) {
      const recipe = response.data.data?.recipe || response.data.recipe_data;
      const recipeId = response.data.data?.recipe_id || response.data.recipe_id;
      
      logTest('Import from Text', 'PASS', `Recipe: "${recipe?.title}" (ID: ${recipeId})`);
      
      return recipeId;
    } else {
      logTest('Import from Text', 'FAIL', response.data.error);
      return null;
    }
  } catch (error) {
    console.error('Text Import Error:', error.response?.data || error.message);
    logTest('Import from Text', 'FAIL', error.response?.data?.error || error.message);
    return null;
  }
}

// Test 5: Delete Recipe
async function testDeleteRecipe(recipeId) {
  logSection('🗑️  TEST 5: DELETE RECIPE (V2)');
  
  if (!recipeId) {
    logTest('Delete Recipe', 'SKIP', 'No recipe ID to delete');
    totalTests--; // Don't count skipped tests
    return;
  }
  
  try {
    log(`DELETE /api/v2/recipes/${recipeId}?user_id=${userId}`, 'blue');
    
    const response = await apiRequest('DELETE', `/api/v2/recipes/${recipeId}?user_id=${userId}`);
    
    if (response.data.success) {
      logTest('Delete Recipe', 'PASS', `Deleted recipe ${recipeId}`);
    } else {
      logTest('Delete Recipe', 'FAIL', response.data.error);
    }
  } catch (error) {
    logTest('Delete Recipe', 'FAIL', error.response?.data?.error || error.message);
  }
}

// Test 6: Search Recipes
async function testSearchRecipes() {
  logSection('🔍 TEST 6: SEARCH RECIPES (V2)');
  
  try {
    log(`GET /api/v2/recipes/search?user_id=${userId}&q=chicken`, 'blue');
    
    const response = await apiRequest('GET', `/api/v2/recipes/search?user_id=${userId}&q=chicken`);
    
    if (response.data.success) {
      const recipes = response.data.data?.recipes || [];
      logTest('Search Recipes', 'PASS', `Found ${recipes.length} recipes matching "chicken"`);
      
      if (recipes.length > 0) {
        log(`  First result: "${recipes[0].title}"`, 'blue');
      }
    } else {
      logTest('Search Recipes', 'FAIL', response.data.error);
    }
  } catch (error) {
    logTest('Search Recipes', 'FAIL', error.response?.data?.error || error.message);
  }
}

// Test 7: Voice Import (Simulated - requires actual audio)
async function testVoiceImport() {
  logSection('🎤 TEST 7: VOICE IMPORT (V2) - SKIPPED');
  
  log('⚠️  Voice import requires actual audio file - testing endpoint availability only', 'yellow');
  
  try {
    // Just check if endpoint exists by sending malformed request
    await apiRequest('POST', '/api/v2/recipes/voice/session/process', {
      user_id: userId
    });
  } catch (error) {
    // We expect this to fail with validation error, not 404
    if (error.response?.status === 400) {
      logTest('Voice Import Endpoint', 'PASS', 'Endpoint exists (validation error expected)');
    } else if (error.response?.status === 404) {
      logTest('Voice Import Endpoint', 'FAIL', 'Endpoint not found');
    } else {
      logTest('Voice Import Endpoint', 'PASS', 'Endpoint exists');
    }
  }
}

// Test 8: OCR Import (Simulated - requires actual image)
async function testOCRImport() {
  logSection('📸 TEST 8: OCR IMPORT (V2) - SKIPPED');
  
  log('⚠️  OCR import requires actual image file - testing endpoint availability only', 'yellow');
  
  try {
    // Just check if endpoint exists
    await apiRequest('POST', '/api/v2/recipes/import/ocr', {
      user_id: userId
    });
  } catch (error) {
    // We expect this to fail with validation error, not 404
    if (error.response?.status === 400) {
      logTest('OCR Import Endpoint', 'PASS', 'Endpoint exists (validation error expected)');
    } else if (error.response?.status === 404) {
      logTest('OCR Import Endpoint', 'FAIL', 'Endpoint not found');
    } else {
      logTest('OCR Import Endpoint', 'PASS', 'Endpoint exists');
    }
  }
}

// Test 9: Community Recipe Claim
async function testClaimRecipe() {
  logSection('🤝 TEST 9: CLAIM COMMUNITY RECIPE (V2)');
  
  log('⚠️  Claim requires a community recipe - testing endpoint availability only', 'yellow');
  
  try {
    // Try to claim a non-existent recipe to test endpoint
    await apiRequest('POST', '/api/v2/community/recipes/99999/claim', {
      user_id: userId
    });
  } catch (error) {
    // We expect this to fail with not found or already claimed, not 404 on endpoint
    if (error.response?.status === 404 && error.response?.data?.error?.includes('Recipe')) {
      logTest('Claim Recipe Endpoint', 'PASS', 'Endpoint exists (recipe not found expected)');
    } else if (error.response?.status === 404) {
      logTest('Claim Recipe Endpoint', 'FAIL', 'Endpoint not found');
    } else {
      logTest('Claim Recipe Endpoint', 'PASS', 'Endpoint exists');
    }
  }
}

// Summary
function printSummary() {
  logSection('📊 TEST SUMMARY');
  
  log(`Total Tests: ${totalTests}`, 'bright');
  log(`Passed: ${passedTests}`, 'green');
  log(`Failed: ${failedTests}`, failedTests > 0 ? 'red' : 'green');
  log(`Success Rate: ${Math.round((passedTests / totalTests) * 100)}%`, 'cyan');
  
  if (failedTests > 0) {
    console.log('\n' + '─'.repeat(80));
    log('FAILED TESTS:', 'red');
    testResults
      .filter(r => r.status === 'FAIL')
      .forEach(r => {
        log(`  ✗ ${r.testName}`, 'red');
        if (r.details) log(`    ${r.details}`, 'yellow');
      });
  }
  
  console.log('\n' + '='.repeat(80));
  
  if (failedTests === 0) {
    log('🎉 ALL TESTS PASSED! V2 MIGRATION SUCCESSFUL!', 'green');
  } else {
    log('⚠️  SOME TESTS FAILED - REVIEW ERRORS ABOVE', 'red');
  }
  
  console.log('='.repeat(80) + '\n');
}

// Main test runner
async function runTests() {
  log('╔═══════════════════════════════════════════════════════════════════════════════╗', 'cyan');
  log('║                     V2 RECIPE API MIGRATION TEST SUITE                       ║', 'cyan');
  log('╚═══════════════════════════════════════════════════════════════════════════════╝', 'cyan');
  
  log(`\nAPI Base URL: ${API_BASE_URL}`, 'blue');
  log(`Test User: ${TEST_USER_EMAIL}\n`, 'blue');
  
  // Step 1: Authenticate
  const authenticated = await authenticate();
  if (!authenticated) {
    log('\n❌ Authentication failed - cannot proceed with tests', 'red');
    process.exit(1);
  }
  
  await sleep(500);
  
  // Step 2: Get User Recipes
  const recipes = await testGetUserRecipes();
  await sleep(500);
  
  // Step 3: Get User Recipes with Stats
  await testGetUserRecipesWithStats();
  await sleep(500);
  
  // Step 4: Import from URL
  const importedRecipeId = await testImportFromURL();
  await sleep(1000); // Give server time to process
  
  // Step 5: Import from Text
  const textRecipeId = await testImportFromText();
  await sleep(1000);
  
  // Step 6: Search Recipes
  await testSearchRecipes();
  await sleep(500);
  
  // Step 7: Voice Import (endpoint check only)
  await testVoiceImport();
  await sleep(500);
  
  // Step 8: OCR Import (endpoint check only)
  await testOCRImport();
  await sleep(500);
  
  // Step 9: Claim Recipe (endpoint check only)
  await testClaimRecipe();
  await sleep(500);
  
  // Step 10: Delete imported recipe (cleanup)
  if (importedRecipeId) {
    await testDeleteRecipe(importedRecipeId);
    await sleep(500);
  }
  
  // Print summary
  printSummary();
  
  // Exit with appropriate code
  process.exit(failedTests > 0 ? 1 : 0);
}

// Run tests
runTests().catch(error => {
  log('\n❌ FATAL ERROR:', 'red');
  console.error(error);
  process.exit(1);
});
