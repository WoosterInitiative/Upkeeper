# TypeScript API Types Generation

This setup automatically generates TypeScript types and client functions from your FastAPI OpenAPI schema using [hey-api/openapi-ts](https://heyapi.vercel.app/).

## Generated Files

The following files are generated in `src/api/`:
- `types.gen.ts` - All TypeScript type definitions
- `sdk.gen.ts` - Client functions for API calls
- `client.gen.ts` - HTTP client configuration
- `index.ts` - Exports barrel file

## Available Scripts

### Development

```bash
# Generate types from running FastAPI server (http://localhost:8102)
npm run generate-types

# Check what would be generated (dry run)
npm run generate-types:check

# Watch for changes in Python files and regenerate types
npm run types:watch
```

### CI/CD

```bash
# Save current OpenAPI schema to ../openapi.json
npm run save-schema

# Generate types from saved schema file (for CI/CD)
npm run generate-types:from-file
```

## Usage in TypeScript

### Using Generated Types

```typescript
import type {
  TrackedItemResponse,
  TrackedItemCreateRequest,
  LogEntryResponse
} from './api/types.gen';

// Use types for function parameters and return values
const createItem = async (item: TrackedItemCreateRequest): Promise<TrackedItemResponse> => {
  // implementation
};
```

### Using Generated Client Functions

```typescript
import {
  listTrackedItemsItemsGet,
  createTrackedItemItemsPost,
  getTrackedItemItemsSlugGet
} from './api/sdk.gen';

// List all tracked items
const items = await listTrackedItemsItemsGet();

// Create a new tracked item
const newItem = await createTrackedItemItemsPost({
  body: {
    name: "My Item",
    attributes: {},
  }
});

// Get specific item by slug
const item = await getTrackedItemItemsSlugGet({
  path: { slug: "my-item" }
});
```

## Development Workflow

1. **Start your FastAPI server** (should be running on http://localhost:8102)
2. **Generate types** after making changes to your FastAPI models:
   ```bash
   npm run generate-types
   ```
3. **Use the generated types** in your React components

## CI/CD Setup

### Option 1: Save Schema (Recommended)

Before your CI/CD runs, save the current schema to a file:

```bash
# In your pre-CI script (when FastAPI server is running)
cd frontend
npm run save-schema
```

This creates `openapi.json` which can be committed to your repository. Then in CI:

```bash
cd frontend
npm install
npm run generate-types:from-file
```

### Option 2: Generate During CI

If you want to generate types during CI, ensure your FastAPI server is running:

```bash
# Start FastAPI server in background
cd backend
python -m upkeeper.main &
sleep 5  # Wait for server to start

# Generate types
cd frontend
npm install
npm run generate-types

# Stop background server
kill %1
```

## Configuration

The generation is configured in `openapi-ts.config.ts`:

```typescript
import { defineConfig } from '@hey-api/openapi-ts';

export default defineConfig({
  client: 'fetch',
  input: process.env.OPENAPI_INPUT || 'http://localhost:8102/openapi.json',
  output: './src/api',
  services: false, // Set to true if you want additional service classes
  schemas: false,  // Set to true if you want JSON schemas
});
```

## Troubleshooting

### Server Not Running
```
❌ Server is not running and no saved schema file found.
💡 Either start the FastAPI server or save a schema file first.
```

**Solution**: Start your FastAPI server or use `npm run save-schema` when the server is running.

### Types Out of Date

If your API types seem out of sync:

1. Ensure your FastAPI server is running with the latest changes
2. Run `npm run generate-types` to regenerate types
3. Check that your FastAPI server is exposing the OpenAPI schema at `/openapi.json`

### CI/CD Failures

- Ensure `openapi.json` is committed to your repository
- Use `npm run generate-types:from-file` in CI instead of `npm run generate-types`
- Make sure the schema file is in the correct location (one level up from frontend/)
