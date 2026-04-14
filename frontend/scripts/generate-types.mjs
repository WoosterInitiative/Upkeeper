#!/usr/bin/env node

import { execSync } from 'child_process';
import { existsSync } from 'fs';
import { join } from 'path';

const SCHEMA_URL = 'http://localhost:8102/openapi.json';
const SCHEMA_FILE = join(process.cwd(), '..', 'openapi_client.json');
const OUTPUT_DIR = './src/api';

function checkServerHealth() {
  try {
    execSync('curl -s http://localhost:8102/health', { stdio: 'pipe' });
    return true;
  } catch {
    return false;
  }
}

function saveSchema() {
  console.log('🔄 Saving OpenAPI schema...');
  try {
    execSync(`curl -s ${SCHEMA_URL} > ${SCHEMA_FILE}`, { stdio: 'inherit' });
    console.log('✅ Schema saved successfully');
  } catch (error) {
    console.error('❌ Failed to save schema:', error.message);
    throw error;
  }
}

function generateTypes(input) {
  console.log('🔄 Generating TypeScript types...');
  try {
    // Set environment variable for input source
    process.env.OPENAPI_INPUT = input;
    execSync(`npx openapi-ts --file ./openapi-ts.config.ts`, {
      stdio: 'inherit'
    });
    console.log('✅ TypeScript types generated successfully');
  } catch (error) {
    console.error('❌ Failed to generate types:', error.message);
    throw error;
  }
}

function main() {
  const args = process.argv.slice(2);
  const isDryRun = args.includes('--dry-run');
  const forceFile = args.includes('--from-file');
  const forceSave = args.includes('--save');

  if (isDryRun) {
    console.log('🔍 Dry run - checking if types would be generated...');
    console.log(`Server running: ${checkServerHealth()}`);
    console.log(`Schema file exists: ${existsSync(SCHEMA_FILE)}`);
    return;
  }

  if (forceSave || (!forceFile && checkServerHealth())) {
    if (forceSave) saveSchema();
    generateTypes(SCHEMA_URL);
  } else if (existsSync(SCHEMA_FILE)) {
    console.log('🔄 Server not running, using saved schema file...');
    generateTypes(SCHEMA_FILE);
  } else {
    console.error('❌ Server is not running and no saved schema file found.');
    console.error('💡 Either start the FastAPI server or save a schema file first.');
    console.error('💡 Use --save to save the current schema for CI/CD use.');
    process.exit(1);
  }
}

main();
