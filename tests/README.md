# Test Suite - TeachBack AI Modal Integration

This directory contains test scripts to verify Modal integration and troubleshoot issues.

## Test Files

### Core Modal Tests

#### `test_modal_functions.py`
**Purpose:** Verify basic Modal connectivity and function availability
**Usage:** `python tests/test_modal_functions.py`
**What it tests:**
- Modal package installation
- Modal credentials (MODAL_TOKEN_ID, MODAL_TOKEN_SECRET)
- Connection to deployed Modal functions
- Basic function execution (`analyze_explanation_modal`, `generate_question_modal`)

**Expected output:**
```
✓ All Modal functions are connected and working!
```

---

#### `test_teaching_agent_modal.py`
**Purpose:** Test TeachingAgent Modal integration
**Usage:** `python tests/test_teaching_agent_modal.py`
**What it tests:**
- TeachingAgent initialization with Modal
- Modal usage in `analyze_explanation()`
- Modal usage in `generate_question()`
- Proper logging output (`[MODAL]` vs `[LOCAL]`)

**Expected output:**
```
[MODAL] Using Modal for explanation analysis...
[MODAL] Analysis completed successfully
[MODAL] Using Modal for question generation...
[MODAL] Question generated successfully
✓ TeachingAgent successfully used Modal functions!
```

---

### Multi-Turn Tests

#### `test_turn_5_issue.py`
**Purpose:** Test multi-turn flow through turn 6
**Usage:** `python tests/test_turn_5_issue.py`
**What it tests:**
- Turns 1-6 complete successfully
- Analytics trigger on turn 5
- Turn 6 works after analytics spawn

**Expected output:**
```
✓ All 6 turns completed successfully!
```

---

#### `test_turn_6_after_analytics.py` ⭐ **Primary Test**
**Purpose:** Comprehensive 10-turn test with analytics
**Usage:** `python tests/test_turn_6_after_analytics.py`
**What it tests:**
- All 10 turns complete successfully
- Analytics spawn on turns 5 and 10
- Modal continues working after each analytics spawn
- No degradation or timeouts

**Expected output:**
```
✓ Successfully completed ALL 10 turns!
Summary:
  - Turn 5: Analytics spawned ✓
  - Turn 6-9: Continued working after first analytics ✓
  - Turn 10: Second analytics spawned ✓
✅ Modal functions worked correctly throughout all turns
```

---

### Additional Tests

#### `test_modal_connection.py`
**Purpose:** Basic Modal connectivity diagnostic
**Usage:** `python tests/test_modal_connection.py`
**What it tests:**
- Modal credentials in environment
- Modal package import
- Function lookup and invocation
- Basic remote function call

---

#### `test_modal_integration.py`
**Purpose:** Comprehensive Modal integration test suite
**Usage:** `python tests/test_modal_integration.py`
**What it tests:**
- Modal availability and imports
- Fallback behavior when Modal disabled
- Parallel execution performance
- Background analytics computation
- Batch session processing
- Import structure validation

**Expected output:**
```
✅ All Modal functions imported successfully
✅ Local execution completed
✅ Modal is faster than sequential execution
✅ Background analytics computation successful
```

---

#### `test_analytics_trigger.py`
**Purpose:** Test analytics computation in isolation
**Usage:** `python tests/test_analytics_trigger.py`
**What it tests:**
- `compute_session_analytics` function
- Analytics data processing
- Background spawning mechanism

---

#### `test_features.py`
**Purpose:** Test general TeachBack AI features
**Usage:** `python tests/test_features.py`
**What it tests:**
- Core application features
- Session management
- Feature integration

---

### Data Files

#### `test_teachback.db`
**Purpose:** Test database for persistent session data
**Type:** SQLite database
**Used by:** Tests that require session persistence
**Note:** Automatically created and managed by tests

---

## Running All Tests

Run all tests in sequence:

```bash
# Quick connectivity check
python tests/test_modal_functions.py

# Verify TeachingAgent integration
python tests/test_teaching_agent_modal.py

# Comprehensive multi-turn test
python tests/test_turn_6_after_analytics.py
```

## Troubleshooting

### If tests fail with "Modal not available"
1. Check environment variables: `echo $MODAL_TOKEN_ID`
2. Verify deployment: `modal app list`
3. Check function list: `modal function list --app teachback-ai`

### If tests show `[LOCAL]` instead of `[MODAL]`
1. Check `mcp_server_debug.log` for errors
2. Verify Modal deployment is current
3. Check for Modal exceptions in traceback

### If tests timeout
1. Check Modal dashboard for function status
2. Verify Anthropic API key in Modal secrets
3. Check network connectivity

## Test Success Criteria

✅ **All tests should:**
- Complete without exceptions
- Show `[MODAL]` log messages (not `[LOCAL]`)
- Complete in < 30 seconds per turn
- Work consistently across multiple runs

❌ **Test failures indicate:**
- Modal deployment issues (connection errors)
- Credential problems (authentication failures)
- Network issues (timeouts, connection refused)
- Code bugs (exceptions, wrong output format)

## Adding New Tests

When adding new tests:
1. Follow the existing pattern (encoding fix, dotenv load)
2. Use descriptive print statements with emojis
3. Include clear success/failure criteria
4. Add entry to this README
5. Test on both Windows and Unix-like systems

## Related Documentation

- [FINAL_FIX_SUMMARY.md](../docs/fixes/FINAL_FIX_SUMMARY.md) - Complete fix documentation
- [QUICK_START_AFTER_FIX.md](../docs/fixes/QUICK_START_AFTER_FIX.md) - How to verify fixes
- [MODAL_TIMEOUT_FIX.md](../docs/fixes/MODAL_TIMEOUT_FIX.md) - Modal routing fix details
- [KNOWLEDGE_GRAPH_TIMEOUT_FIX.md](../docs/fixes/KNOWLEDGE_GRAPH_TIMEOUT_FIX.md) - KG timeout fix details
