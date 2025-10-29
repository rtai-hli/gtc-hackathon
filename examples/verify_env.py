#!/usr/bin/env python3
"""
Verify environment variable loading from .env file
"""

import os

# Try to load .env
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ python-dotenv is installed and load_dotenv() executed")
except ImportError:
    print("✗ python-dotenv is NOT installed")
    print("  Install with: pip install python-dotenv")
    exit(1)

# Check for API keys
nvidia_key = os.getenv("NVIDIA_API_KEY")
ngc_key = os.getenv("NGC_API_KEY")

print("\nEnvironment Variables Check:")
print("=" * 80)

if nvidia_key:
    print(f"✓ NVIDIA_API_KEY found: {nvidia_key[:20]}...")
else:
    print("✗ NVIDIA_API_KEY not found")

if ngc_key:
    print(f"✓ NGC_API_KEY found: {ngc_key[:20]}...")
else:
    print("✗ NGC_API_KEY not found")

# Check .env file exists
import os.path
env_path = os.path.join(os.getcwd(), '.env')
if os.path.exists(env_path):
    print(f"\n✓ .env file exists at: {env_path}")
else:
    print(f"\n✗ .env file NOT found at: {env_path}")

if nvidia_key or ngc_key:
    print("\n" + "=" * 80)
    print("SUCCESS: Environment variables are being loaded correctly!")
    print("=" * 80)
    exit(0)
else:
    print("\n" + "=" * 80)
    print("FAILURE: Environment variables are NOT being loaded")
    print("=" * 80)
    print("\nTroubleshooting steps:")
    print("1. Ensure .env file exists in current directory")
    print("2. Ensure .env file has correct format (KEY=value, no quotes)")
    print("3. Install python-dotenv: pip install python-dotenv")
    exit(1)
