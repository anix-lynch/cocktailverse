# 🔧 Sandbox Access Fix - Universal Secret Loading

## Problem

Some Cursor AI instances are **sandboxed** and can't access files outside the workspace (like `~/.config/secrets/global.env`), while others can. This causes inconsistent behavior.

## Solution

Use **workspace-relative secret loading** that works in both environments.

---

## ✅ Universal Secret Loader

### Python Usage

```python
from scripts.get_secret import get_secret

# Get a secret (tries multiple locations automatically)
api_key = get_secret('GOOGLE_MAPS_API_KEY')
project_id = get_secret('PROJECT_ID', default='maps-platform-20251011-140544')
```

**What it does:**
1. Checks environment variables first (highest priority)
2. Tries `~/.config/secrets/global.env` (if accessible)
3. Tries `.env` in project root (always accessible)
4. Returns default if not found

### Shell Script Usage

```bash
# Load secrets (works in both sandboxed and non-sandboxed)
source scripts/load_secrets.sh

# Now all secrets are available
echo $GOOGLE_MAPS_API_KEY
```

---

## 📁 Secret File Priority

The loaders try these locations **in order**:

1. **Environment variables** (already set)
2. `~/.config/secrets/global.env` (if accessible)
3. `~/.secrets/global.env` (alternative location)
4. `./.env` (project root - **always accessible**)
5. `./.env.local` (local overrides)
6. `../.env` (parent directory)

**First match wins!**

---

## 🔄 Migration Guide

### Before (Breaks in Sandbox):
```python
# ❌ This fails in sandboxed environments
with open(os.path.expanduser('~/.config/secrets/global.env')) as f:
    # ...
```

### After (Works Everywhere):
```python
# ✅ This works in both sandboxed and non-sandboxed
from scripts.get_secret import get_secret
api_key = get_secret('GOOGLE_MAPS_API_KEY')
```

---

## 🎯 Best Practice

**Always use the universal loader** - it handles sandbox detection automatically:

```python
# ✅ Good - works everywhere
from scripts.get_secret import get_secret
SECRET = get_secret('SECRET_NAME', default='fallback')

# ❌ Bad - breaks in sandbox
import os
with open(os.path.expanduser('~/.config/secrets/global.env')) as f:
    # ...
```

---

## 🧪 Testing

Test if you're in a sandboxed environment:

```bash
# Test script access
python scripts/get_secret.py GOOGLE_MAPS_API_KEY

# Test shell loader
source scripts/load_secrets.sh && echo $GOOGLE_MAPS_API_KEY
```

---

## 📝 For Cursor AI Assistants

**When accessing secrets, always use:**

```python
from scripts.get_secret import get_secret
```

**Never assume:**
- ❌ `~/.config/secrets/global.env` is accessible
- ❌ Filesystem access outside workspace
- ❌ Home directory access

**Always:**
- ✅ Use `scripts/get_secret.py`
- ✅ Check multiple locations
- ✅ Provide fallbacks
- ✅ Handle PermissionError gracefully

---

## 🔍 Why This Happens

**Sandboxed Environment:**
- Limited filesystem access
- Only workspace directory accessible
- Security feature to prevent data leaks

**Non-Sandboxed Environment:**
- Full filesystem access
- Can read `~/.config/secrets/global.env`
- More permissive (for local development)

**Solution:** Code that works in **both** by trying multiple locations.

---

**Status:** ✅ Fixed - Works in both sandboxed and non-sandboxed environments

