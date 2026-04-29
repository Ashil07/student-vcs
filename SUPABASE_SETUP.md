# Supabase Setup Guide for Student VCS

## 1. Create a Supabase Project

1. Go to [supabase.com](https://supabase.com) and sign in (or sign up)
2. Click **New Project**
3. Choose a name (e.g., `student-vcs`)
4. Pick a region close to you
5. Set a database password (save this!)
6. Wait for the project to be created (~2 minutes)

## 2. Get Your API Keys

1. In your project dashboard, go to **Project Settings > API**
2. Copy these values:
   - **URL** (e.g., `https://abcdefgh12345678.supabase.co`)
   - **anon public** key (starts with `eyJ...`)
   - **service_role secret** key (starts with `eyJ...`)

## 3. Configure Environment Variables

Create a file named `.env` in the project root:

```bash
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-role-key-here
USE_SUPABASE=true
```

> **Security:** Never commit `.env` to Git. It's already in `.gitignore`.

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `supabase` (Python client)
- `python-dotenv` (loads .env file)
- `python-jose` (JWT verification)
- `psycopg2-binary` (direct PostgreSQL connections)

## 5. Run the Schema Setup Script

```bash
python scripts/setup_supabase.py
```

It will ask for your **database password** (from step 1). This creates all tables, indexes, and Row Level Security policies.

## 6. Create a Storage Bucket (Optional)

For blob storage instead of local filesystem:

1. In Supabase dashboard, go to **Storage**
2. Click **New bucket**
3. Name: `vcs-objects`
4. Set **public** to OFF
5. Click **Create bucket**

## 7. Start the API Server

```bash
uvicorn api.main:app --reload --port 8000
```

## 8. Test with curl or Postman

### Health check
```bash
curl http://localhost:8000/
```

### Register a user (via Supabase Auth REST API)
```bash
curl -X POST "https://your-project-ref.supabase.co/auth/v1/signup" \
  -H "apikey: your-anon-key" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'
```

### Sign in to get a JWT
```bash
curl -X POST "https://your-project-ref.supabase.co/auth/v1/token?grant_type=password" \
  -H "apikey: your-anon-key" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'
```

Copy the `access_token` from the response.

### Init a repo (cloud)
```bash
curl -X POST "http://localhost:8000/v2/init" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"repo_name": "my-project"}'
```

### Create a commit (cloud)
```bash
curl -X POST "http://localhost:8000/v2/commit" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "First cloud commit", "repo_name": "my-project"}'
```

### View log (cloud)
```bash
curl "http://localhost:8000/v2/log?repo_name=my-project" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### List branches (cloud)
```bash
curl "http://localhost:8000/v2/branches?repo_name=my-project" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 9. React Frontend + Supabase (Direct Connection)

Your React app can talk directly to Supabase, bypassing your backend entirely for many operations.

### Install Supabase JS client
```bash
cd ui
npm install @supabase/supabase-js
```

### Create `src/supabase.js`
```javascript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseKey = import.meta.env.VITE_SUPABASE_KEY

export const supabase = createClient(supabaseUrl, supabaseKey)
```

### Add to `.env` in `ui/` folder
```
VITE_SUPABASE_URL=https://your-project-ref.supabase.co
VITE_SUPABASE_KEY=your-anon-key-here
```

### Example: Sign up
```javascript
import { supabase } from './supabase'

async function signUp(email, password) {
  const { data, error } = await supabase.auth.signUp({ email, password })
  if (error) console.error(error)
  else console.log(data)
}
```

### Example: Query commits (RLS-protected)
```javascript
async function getCommits(repoId) {
  const { data, error } = await supabase
    .from('commits')
    .select('*')
    .eq('repo_id', repoId)
    .order('timestamp', { ascending: false })

  if (error) console.error(error)
  return data
}
```

> The `commits` table has RLS enabled — users automatically only see their own commits.

## Architecture

```
+----------------+     +-------------------+     +------------------+
|   React UI     |     |   FastAPI Server  |     |   Supabase       |
|                |     |   (Python)          |     |   (PostgreSQL)   |
|                |<--->|   /v2/* endpoints  |<--->|   + Auth         |
|                |     |   JWT verification |     |   + Storage      |
|                |     |   + local SQLite   |     |   + Realtime     |
|   OR direct    |     |   fallback         |     |                  |
|   Supabase JS  |<--->|                    |     |                  |
+----------------+     +-------------------+     +------------------+
```

## Local vs Cloud Mode

| Mode | Trigger | Storage | Auth |
|------|---------|---------|------|
| **Local** | `USE_SUPABASE=false` (or missing) | SQLite + local filesystem | None |
| **Cloud** | `USE_SUPABASE=true` + valid keys | Supabase PostgreSQL + optional Storage | JWT via Supabase Auth |

Both modes work simultaneously. The CLI always uses local SQLite. The API serves both `/` (local) and `/v2/` (cloud) endpoints.

## Troubleshooting

### "Supabase is not configured" error
- Check `.env` has `USE_SUPABASE=true`
- Verify `SUPABASE_URL` and `SUPABASE_KEY` are set
- Restart the API server after changing `.env`

### "Invalid token" error
- Ensure you're sending `Authorization: Bearer <token>`
- Token may have expired — get a new one via sign-in
- Check that the anon key matches your Supabase project

### PostgreSQL connection fails in setup script
- Make sure you entered the correct **database password** (not the API key)
- Check your Supabase dashboard: Settings > Database > Connection String
- Ensure your IP is not blocked (Supabase has connection pooling settings)
