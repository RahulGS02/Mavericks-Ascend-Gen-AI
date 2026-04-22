#!/usr/bin/env node

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🚀 Maverick Insights - Project Setup\n');

// Create directory structure
const dirs = [
  'apps/web',
  'apps/api',
  'packages/shared',
  'docs'
];

console.log('📁 Creating directory structure...');
dirs.forEach(dir => {
  const dirPath = path.join(process.cwd(), dir);
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
    console.log(`   ✓ Created ${dir}`);
  } else {
    console.log(`   ○ ${dir} already exists`);
  }
});

console.log('\n✅ Directory structure created!\n');
console.log('📝 Next steps:');
console.log('   1. cd apps/web && npx create-next-app@latest . --typescript --tailwind --app --src-dir --import-alias "@/*"');
console.log('   2. cd apps/api && python -m venv venv && pip install fastapi uvicorn');
console.log('   3. Set up environment variables');
console.log('\n   Run: npm run setup:web to setup frontend');
console.log('   Run: npm run setup:api to setup backend\n');
