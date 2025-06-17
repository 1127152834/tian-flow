#!/usr/bin/env node
/**
 * Test script to verify API URL resolution
 */

// Simulate the environment
process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8000/api';

// Mock the env module
const env = {
  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL
};

// Copy the resolveServiceURL function
function resolveServiceURL(path) {
  let BASE_URL = env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/";
  if (!BASE_URL.endsWith("/")) {
    BASE_URL += "/";
  }
  return new URL(path, BASE_URL).toString();
}

// Test the URL resolution
console.log('🧪 Testing API URL Resolution');
console.log('=' * 40);

const testPaths = [
  'text2sql/statistics',
  'text2sql/generate',
  'text2sql/training',
  'text2sql/health',
  'database-datasources'
];

testPaths.forEach(path => {
  const resolvedUrl = resolveServiceURL(path);
  console.log(`📍 ${path} -> ${resolvedUrl}`);
});

console.log('\n✅ All URLs should point to localhost:8000, not localhost:3000/3001');

// Test a simple fetch to the health endpoint
async function testHealthEndpoint() {
  try {
    console.log('\n🏥 Testing health endpoint...');
    const url = resolveServiceURL('text2sql/health');
    console.log(`Fetching: ${url}`);
    
    const response = await fetch(url);
    console.log(`Status: ${response.status} ${response.statusText}`);
    
    if (response.ok) {
      const data = await response.json();
      console.log('Response:', data);
    } else {
      console.log('Error response:', await response.text());
    }
  } catch (error) {
    console.log('Fetch error:', error.message);
  }
}

// Run the test
testHealthEndpoint();
