import { defineConfig } from '@hey-api/openapi-ts';

export default defineConfig({
  client: 'fetch',
  input: process.env.OPENAPI_INPUT || 'http://localhost:8102/openapi.json',
  output: './src/api',
  services: false,
  schemas: false,
});
