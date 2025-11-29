# TeachBack AI - Project Organization

## Directory Structure

```
teachback-ai/
├── docs/                      # Documentation
│   ├── fixes/                 # Fix documentation
│   │   ├── README.md          # Fix documentation index
│   │   ├── FINAL_FIX_SUMMARY.md
│   │   ├── QUICK_START_AFTER_FIX.md
│   │   ├── MODAL_TIMEOUT_FIX.md
│   │   └── KNOWLEDGE_GRAPH_TIMEOUT_FIX.md
│   └── modal/                 # Modal integration docs
│       ├── README.md          # Modal documentation index
│       ├── MODAL_QUICKSTART.md
│       ├── MODAL_DEPLOYMENT_CHECKLIST.md
│       ├── MODAL_INTEGRATION.md
│       ├── MODAL_IMPLEMENTATION_SUMMARY.md
│       ├── MODAL_VERIFICATION.md
│       └── MODAL_SUCCESS.md
│
├── tests/                     # Test suite
│   ├── README.md              # Test documentation
│   ├── test_modal_functions.py
│   ├── test_teaching_agent_modal.py
│   ├── test_modal_connection.py
│   ├── test_modal_integration.py
│   ├── test_analytics_trigger.py
│   ├── test_features.py
│   ├── test_turn_5_issue.py
│   ├── test_turn_6_after_analytics.py
│   └── test_teachback.db      # Test database
│
├── logs/                      # Application logs
│   └── (log files excluded from git)
│
├── src/                       # Source code
│   ├── agents/                # AI agents
│   │   └── teaching_agent.py  # Main teaching agent (Modal-enabled)
│   ├── services/              # Business logic
│   │   ├── knowledge_graph.py # KG service (timeout-protected)
│   │   └── ...
│   ├── ui/                    # User interface
│   │   ├── handlers.py        # UI event handlers
│   │   └── ...
│   └── mcp/                   # MCP client/server
│       └── client_wrapper.py
│
├── modal_app.py               # Modal function definitions
├── mcp_server.py              # MCP server (with debug logging)
├── app.py                     # Main Gradio application
├── .env                       # Environment variables (not in git)
├── .gitignore                 # Git ignore patterns
└── requirements.txt           # Python dependencies
```

## Key Documents

### For Users

| Document | Purpose | Location |
|----------|---------|----------|
| **README.md** | Main project overview | Root |
| **QUICK_START_AFTER_FIX.md** | How to use after fixes | `docs/fixes/` |
| **Test README** | How to run tests | `tests/README.md` |

### For Developers

| Document | Purpose | Location |
|----------|---------|----------|
| **FINAL_FIX_SUMMARY.md** | Complete fix overview | `docs/fixes/` |
| **MODAL_TIMEOUT_FIX.md** | Modal routing technical details | `docs/fixes/` |
| **KNOWLEDGE_GRAPH_TIMEOUT_FIX.md** | KG timeout technical details | `docs/fixes/` |
| **Fix README** | Fix documentation index | `docs/fixes/README.md` |

### Modal Integration Documentation

Complete Modal setup and integration guides:

| Document | Purpose | Location |
|----------|---------|----------|
| **Modal README** | Documentation index | `docs/modal/README.md` |
| **MODAL_QUICKSTART.md** | Quick 3-step setup | `docs/modal/` |
| **MODAL_DEPLOYMENT_CHECKLIST.md** | Step-by-step deployment | `docs/modal/` |
| **MODAL_INTEGRATION.md** | Complete technical guide | `docs/modal/` |
| **MODAL_IMPLEMENTATION_SUMMARY.md** | Implementation overview | `docs/modal/` |
| **MODAL_VERIFICATION.md** | Deployment verification | `docs/modal/` |
| **MODAL_SUCCESS.md** | Success confirmation | `docs/modal/` |

## Important Files by Category

### Configuration Files
- `.env` - Environment variables (Modal/Anthropic credentials)
- `.gitignore` - Git ignore patterns
- `requirements.txt` - Python dependencies
- `mcp_config.json` - MCP configuration

### Modal Files
- `modal_app.py` - Modal function definitions
- `deploy_modal.py` - Modal deployment script
- `modal_setup.py` - Modal setup utilities

### Application Entry Points
- `app.py` - Main Gradio application
- `mcp_server.py` - MCP server
- `modal_app.py` - Modal functions

### Core Source Code
- `src/agents/teaching_agent.py` - **Modified for Modal**
- `src/services/knowledge_graph.py` - **Modified with timeout**
- `src/ui/handlers.py` - **Modified for error handling**
- `mcp_server.py` - **Modified with logging**

## Testing Workflow

### Quick Test (2 minutes)
```bash
python tests/test_modal_functions.py
```

### Medium Test (5 minutes)
```bash
python tests/test_teaching_agent_modal.py
```

### Full Test (10 minutes)
```bash
python tests/test_turn_6_after_analytics.py
```

### Application Test
```bash
python app.py
# Then test through UI
```

## Debugging Workflow

### Check Logs
```bash
# MCP server logs
cat logs/mcp_server_debug.log

# Application logs
# (shown in console where app.py runs)
```

### Verify Modal
```bash
# Check Modal deployment
modal app list
modal function list --app teachback-ai

# Check environment
echo $MODAL_TOKEN_ID
echo $ANTHROPIC_API_KEY
```

### Run Diagnostics
```bash
# Test Modal connectivity
python tests/test_modal_functions.py

# Test full flow
python tests/test_turn_6_after_analytics.py
```

## Development Workflow

### Making Changes

1. **Modify code** in `src/`
2. **Run tests** to verify
   ```bash
   python tests/test_turn_6_after_analytics.py
   ```
3. **Check logs** for issues
   ```bash
   cat logs/mcp_server_debug.log
   ```
4. **Test in app**
   ```bash
   python app.py
   ```

### Adding New Features

1. **Write code** in appropriate module
2. **Add tests** in `tests/`
3. **Update documentation** in `docs/`
4. **Verify Modal integration** if applicable
5. **Run full test suite**

### Deploying Changes

1. **Update Modal** if functions changed
   ```bash
   modal deploy modal_app.py
   ```
2. **Test deployment**
   ```bash
   python tests/test_modal_functions.py
   ```
3. **Run application**
   ```bash
   python app.py
   ```

## Git Workflow

### Ignored Files
The following are automatically ignored:
- `logs/` - Log files
- `.env` - Environment variables
- `venv/` - Virtual environment
- `__pycache__/` - Python cache
- `*.log` - Log files
- `mcp_server_debug.log` - Debug logs

### Tracked Files
Important files that **should** be in git:
- All source code (`src/`)
- All documentation (`docs/`, `*.md`)
- All tests (`tests/`)
- Configuration templates (`.env.example`)
- Requirements (`requirements.txt`)
- Modal definitions (`modal_app.py`)

## Maintenance Checklist

### Weekly
- [ ] Run full test suite
- [ ] Check logs for warnings
- [ ] Verify Modal usage in production

### Monthly
- [ ] Review and clean logs
- [ ] Update dependencies
- [ ] Check Modal costs/usage
- [ ] Review error patterns

### After Each Change
- [ ] Run relevant tests
- [ ] Update documentation
- [ ] Check logs for new errors
- [ ] Verify Modal still works

## Support & Troubleshooting

### First Steps
1. Check `logs/mcp_server_debug.log`
2. Run `tests/test_modal_functions.py`
3. Verify `.env` has credentials
4. Check Modal deployment status

### Common Issues
- **"Modal not available"**: Check deployment and credentials
- **Timeouts**: Check network and Modal status
- **`[LOCAL]` in logs**: Modal fallback triggered, check errors
- **Import errors**: Check virtual environment and dependencies

### Getting Help
1. Check documentation in `docs/fixes/`
2. Review test output from `tests/`
3. Examine logs in `logs/`
4. Check Modal dashboard for function status

---

**Last Updated:** 2025-11-28
**Version:** 1.0 (Post-timeout-fix)
