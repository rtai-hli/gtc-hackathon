# Quick Start Guide - NVIDIA Nemotron Integration

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `python-dotenv>=1.0.0` - For loading .env files (REQUIRED)
- `openai>=1.0.0` - For NVIDIA API client
- `fastapi>=0.104.0` - For microservices (optional)
- `uvicorn>=0.24.0` - For microservices (optional)
- `httpx>=0.24.0` - For async HTTP (optional)

### 2. Verify Environment Variables

Your API key is already configured in `.env`. Verify it's being loaded correctly:

```bash
# Run verification script
python verify_env.py

# Expected output:
# ✓ python-dotenv is installed and load_dotenv() executed
# ✓ NVIDIA_API_KEY found: nvapi-kLp-HL-Q-PfZV7...
# SUCCESS: Environment variables are being loaded correctly!
```

**Troubleshooting**: If you get "No API key found", see `ENV_FIX_GUIDE.md`

## Testing

### Run the Test Suite

```bash
python test_nemotron.py
```

This will run 4 tests:
1. LLM wrapper initialization
2. Simple query (non-streaming)
3. Streaming with reasoning display
4. Agent integration

### Run the Full Demo

```bash
# Full demo with visualization
python demo.py

# Simple text-only output
python demo.py --simple

# Interactive mode (step-by-step)
python demo.py --interactive
```

## What Was Changed

### Files Modified

1. **`.env`**: Added `NVIDIA_API_KEY` for compatibility
2. **`requirements.txt`**: Added `openai>=1.0.0` dependency
3. **`agents/base.py`**: Added `llm_reason()` method and conversation history
4. **`agents/commander.py`**: Integrated LLM for root cause analysis
5. **`demo.py`**: Added LLM client initialization

### Files Created

1. **`agents/llm_wrapper.py`**: Clean async wrapper for NVIDIA Nemotron API
2. **`test_nemotron.py`**: Comprehensive test suite
3. **`NVIDIA_INTEGRATION.md`**: Detailed integration documentation
4. **`QUICKSTART_GUIDE.md`**: This file

For more details, see `NVIDIA_INTEGRATION.md`.
