#!/usr/bin/env node
// @ts-nocheck

/**
 * 前端错误检查脚本
 * 用于主动发现所有 TypeScript 和构建错误
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🔍 开始检查前端错误...\n');

// 1. TypeScript 类型检查
console.log('📝 1. 检查 TypeScript 类型错误...');
try {
  execSync('npx tsc --noEmit --skipLibCheck', { 
    stdio: 'pipe',
    cwd: process.cwd()
  });
  console.log('✅ TypeScript 类型检查通过');
} catch (error) {
  console.log('❌ 发现 TypeScript 错误:');
  console.log(String(error));
}

// 2. ESLint 检查
console.log('\n🔧 2. 检查 ESLint 错误...');
try {
  execSync('npx eslint src --ext .ts,.tsx --max-warnings 0', { 
    stdio: 'pipe',
    cwd: process.cwd()
  });
  console.log('✅ ESLint 检查通过');
} catch (error) {
  console.log('❌ 发现 ESLint 错误:');
  console.log(String(error));
}

// 3. Next.js 构建检查
console.log('\n🏗️  3. 检查 Next.js 构建错误...');
try {
  execSync('npx next build --no-lint', { 
    stdio: 'pipe',
    cwd: process.cwd()
  });
  console.log('✅ Next.js 构建检查通过');
} catch (error) {
  console.log('❌ 发现构建错误:');
  console.log(String(error));
}

// 4. 检查导入路径
console.log('\n📦 4. 检查导入路径一致性...');
const srcDir = path.join(process.cwd(), 'src');
let importErrors = [];

function checkImports(dir) {
  const files = fs.readdirSync(dir);
  
  for (const file of files) {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    
    if (stat.isDirectory()) {
      checkImports(filePath);
    } else if (file.endsWith('.ts') || file.endsWith('.tsx')) {
      const content = fs.readFileSync(filePath, 'utf8');
      const lines = content.split('\n');
      
      lines.forEach((line, index) => {
        if (line.includes('import') && line.includes('@/')) {
          importErrors.push({
            file: filePath.replace(process.cwd(), '.'),
            line: index + 1,
            content: line.trim()
          });
        }
      });
    }
  }
}

checkImports(srcDir);

if (importErrors.length > 0) {
  console.log('❌ 发现导入路径错误 (应使用 ~/ 而不是 @/):');
  importErrors.forEach(error => {
    console.log(`  ${error.file}:${error.line} - ${error.content}`);
  });
} else {
  console.log('✅ 导入路径检查通过');
}

console.log('\n🎉 错误检查完成!');
