# Quick Reference - GTC Hackathon Project

## 🚀 Running the Demos

### Incident Response War Room (CLI)
```bash
# Full demo with visualization
python demo.py

# Simple output mode
python demo.py --simple

# Interactive step-by-step
python demo.py --interactive
```

### Nonprofit Web Interface
```bash
# Start Flask server
python web_app.py

# Visit in browser
open http://localhost:5000
```

## 📁 Where to Find Things

### Core Code
- **Agents**: `agents/` - All agent framework code
- **Scenarios**: `scenarios/` - Pre-configured incident scenarios
- **Templates**: `templates/` - Web UI HTML templates

### Development
- **Examples**: `examples/` - Example scripts and utilities
- **Tests**: `tests/` - Test suites and model comparisons
- **Documentation**: `docs/` - All project documentation (23 files)

### Generated/Output
- **Incidents**: `incidents/` - Generated incident reports (JSON)
- **Assets**: `assets/` - Static assets and images

### Research
- **Jupyter**: `jupyter/` - Notebooks and experimental code

## 🔑 Key Files

| File | Purpose |
|------|---------|
| `demo.py` | Main CLI demo entry point |
| `web_app.py` | Web UI demo (Flask app) |
| `README.md` | Project overview and setup |
| `requirements.txt` | Python dependencies |
| `.env` | Environment variables (API keys) |

## 📚 Essential Documentation

| Document | Location | Purpose |
|----------|----------|---------|
| Quick Start | `docs/QUICK_START_49B.md` | Get running in 30 seconds |
| Architecture | `docs/AGENT_ARCHITECTURE.md` | System design with diagrams |
| Web UI Guide | `docs/WEB_UI_GUIDE.md` | Web interface documentation |
| Troubleshooting | `docs/TROUBLESHOOTING_SUMMARY.md` | Common issues & fixes |

## 🛠️ Common Tasks

### Add a New Agent
1. Create file in `agents/`
2. Extend `BaseAgent` from `agents/base.py`
3. Register in demo runner

### Add Documentation
Place in `docs/` folder

### Add Tests
Place in `tests/` folder

### Add Examples
Place in `examples/` folder

## 🌐 Project URLs

- Deployed: `gala-minigame.vercel.app`
- Local Web: `http://localhost:5000`
- Supabase: Configured via Vercel env vars

## 📊 Project Stats

- **Agents**: 3 core agent files
- **Docs**: 23 documentation files
- **Templates**: 7 HTML templates
- **Tests**: 3 test suites
- **Examples**: 5 example scripts
- **Scenarios**: 1 pre-configured incident

## 🔄 Recent Changes

See `ORGANIZATION_SUMMARY.md` for details on the recent reorganization.

## 💡 Quick Tips

1. **Environment Setup**: Copy `.env.example` to `.env` and add your NVIDIA API key
2. **Dependencies**: Run `pip install -r requirements.txt`
3. **Testing**: Both demos tested and working after reorganization
4. **Documentation**: All docs now in `docs/` - README links updated
