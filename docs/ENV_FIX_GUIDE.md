# Environment Variable Loading Fix

## Problem

**Issue**: "No API key found" warning despite keys being present in `.env` file.

**Root Cause**: Python does not automatically load `.env` files. The `python-dotenv` package is required to read environment variables from `.env` files.

## Solution

### 1. Install python-dotenv

```bash
pip install python-dotenv
```

Or install all dependencies:

```bash
pip install -r requirements.txt
```

### 2. Verify the Fix

Run the verification script:

```bash
python verify_env.py
```

**Expected output:**
```
✓ python-dotenv is installed and load_dotenv() executed

Environment Variables Check:
================================================================================
✓ NVIDIA_API_KEY found: nvapi-kLp-HL-Q-PfZV7...
✓ NGC_API_KEY found: nvapi-kLp-HL-Q-PfZV7...

✓ .env file exists at: /Users/henanli/dev/gtc-hackathon/.env

================================================================================
SUCCESS: Environment variables are being loaded correctly!
================================================================================
```

### 3. Test the Application

```bash
# Test the LLM wrapper
python test_nemotron.py

# Run the demo
python demo.py
```

## What Was Fixed

### Files Modified

1. **`requirements.txt`**: Added `python-dotenv>=1.0.0`
2. **`agents/llm_wrapper.py`**: Added `.env` loading at module import
3. **`demo.py`**: Added `.env` loading at startup
4. **`test_nemotron.py`**: Added `.env` loading at startup

### Files Created

1. **`verify_env.py`**: Environment variable verification script
2. **`ENV_FIX_GUIDE.md`**: This file

## Code Changes

All Python files that need environment variables now include:

```python
# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed. Run: pip install python-dotenv")
```

This:
- ✅ Loads `.env` file if `python-dotenv` is installed
- ✅ Gracefully handles missing `python-dotenv`
- ✅ Provides clear error message if package is missing

## How It Works

### Before Fix

```python
import os
api_key = os.getenv("NVIDIA_API_KEY")  # Returns None!
```

**Why?** Python's `os.getenv()` only reads from:
- System environment variables (exported in shell)
- Environment variables set by parent process
- **NOT from .env files**

### After Fix

```python
from dotenv import load_dotenv
load_dotenv()  # Reads .env and loads into os.environ

import os
api_key = os.getenv("NVIDIA_API_KEY")  # Now works!
```

## Alternative: Manual Export

If you don't want to use `python-dotenv`, you can manually export:

```bash
# Option 1: Export in current shell
export NVIDIA_API_KEY="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"
python demo.py

# Option 2: Inline for single command
NVIDIA_API_KEY="nvapi-..." python demo.py

# Option 3: Source .env file (requires special format)
set -a
source .env
set +a
python demo.py
```

However, **using `python-dotenv` is recommended** because:
- ✅ Automatic loading
- ✅ No manual export needed
- ✅ Works consistently across environments
- ✅ Standard Python practice

## Troubleshooting

### Still getting "No API key found"?

**Check 1**: Verify python-dotenv is installed
```bash
python -c "from dotenv import load_dotenv; print('OK')"
```

**Check 2**: Verify .env file format
```bash
cat .env
# Should show:
# NVIDIA_API_KEY=nvapi-...
# No quotes, no spaces around =
```

**Check 3**: Verify .env file location
```bash
ls -la .env
# Should be in the same directory as demo.py
```

**Check 4**: Test environment loading
```bash
python verify_env.py
```

### ImportError: No module named 'dotenv'

Install the package:
```bash
pip install python-dotenv
```

### "python-dotenv is installed" but still no API key

1. Check .env file is in the correct directory (where you run the script)
2. Check .env file has correct format (no extra spaces, quotes, or special characters)
3. Try absolute path:
   ```python
   from dotenv import load_dotenv
   load_dotenv('/Users/henanli/dev/gtc-hackathon/.env')
   ```

## Best Practices

### ✅ Do

- Use `python-dotenv` for development
- Keep `.env` file in project root
- Add `.env` to `.gitignore` (security)
- Use `load_dotenv()` at application entry point
- Provide clear error messages if keys missing

### ❌ Don't

- Commit `.env` file to git (contains secrets!)
- Rely on manual exports in production
- Use quotes in `.env` file values
- Put spaces around `=` in `.env` file

## Production Deployment

For production, use proper secret management:

- **Kubernetes**: Use Secrets
- **Docker**: Use environment variables or secrets
- **Cloud**: Use managed secret services (AWS Secrets Manager, Azure Key Vault, etc.)
- **Heroku/Vercel**: Use config vars/environment variables

The code already handles this - it will use `python-dotenv` in development and system environment variables in production.

## Summary

**Problem**: `.env` file not being loaded → API keys not accessible

**Solution**: Install `python-dotenv` and add `load_dotenv()` to application files

**Verification**: Run `python verify_env.py` to confirm fix

**Next Steps**: Run `python demo.py` and `python test_nemotron.py` to test the application
