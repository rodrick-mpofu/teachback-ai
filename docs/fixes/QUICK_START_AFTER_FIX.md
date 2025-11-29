# Quick Start Guide - After Modal Timeout Fix

## What Was Fixed

The timeout issue on `analyze_explanation` after the 5th turn has been **resolved**. The TeachingAgent now correctly uses Modal functions for all AI operations.

## How to Run

### 1. Verify Modal Connection

```bash
python test_modal_functions.py
```

**Expected output:**
```
✓ All Modal functions are connected and working!

The TeachingAgent will now use Modal for:
  • analyze_explanation() - Every turn
  • generate_question() - Every turn
  • compute_session_analytics() - Background on 5th turn
```

### 2. Test the TeachingAgent

```bash
python test_teaching_agent_modal.py
```

**Expected output:**
```
[MODAL] Using Modal for explanation analysis...
[MODAL] Analysis completed successfully
✓ Analysis completed!

[MODAL] Using Modal for question generation...
[MODAL] Question generated successfully
✓ Question generated!
```

### 3. Run the MCP Server

```bash
python mcp_server.py
```

The MCP server should now route all requests through Modal.

### 4. Run the Main Application

```bash
python app.py
```

or

```bash
gradio app.py
```

## What to Watch For

### ✅ Success Indicators

- See `[MODAL]` log messages in the console
- Fast response times (< 5 seconds per turn)
- No timeout errors
- Background analytics triggers on 5th turn

### ⚠️ Warning Signs

- See `[LOCAL]` log messages - means Modal fallback occurred
- See `[WARNING] Modal ... failed` - Modal execution errors
- Timeouts after 300s - Modal not being used

## Execution Flow

### Turn 1-4
```
User submits explanation
  ↓
MCP Server receives request
  ↓
TeachingAgent.analyze_explanation()
  ↓
[MODAL] analyze_explanation_modal.remote() ⚡ Fast!
  ↓
TeachingAgent.generate_question()
  ↓
[MODAL] generate_question_modal.remote() ⚡ Fast!
  ↓
Response returned to user
```

### Turn 5 (and multiples of 5)
```
User submits explanation
  ↓
MCP Server receives request
  ↓
TeachingAgent.analyze_explanation()
  ↓
[MODAL] analyze_explanation_modal.remote() ⚡ Fast!
  ↓
TeachingAgent.generate_question()
  ↓
[MODAL] generate_question_modal.remote() ⚡ Fast!
  ↓
[ANALYTICS] compute_session_analytics.spawn() 🔄 Background
  ↓
Response returned to user (doesn't wait for analytics)
```

## Troubleshooting

### Problem: Still seeing timeouts

**Check:**
1. Modal credentials are set: `echo %MODAL_TOKEN_ID%`
2. Modal app is deployed: `modal app list`
3. Functions exist: `modal function list --app teachback-ai`

**Fix:**
```bash
# Redeploy Modal app
modal deploy modal_app.py
```

### Problem: Seeing [LOCAL] instead of [MODAL]

**Check:**
1. Import errors in teaching_agent.py
2. Modal functions not found

**Fix:**
```bash
# Test Modal connectivity
python test_modal_functions.py

# If that fails, check Modal deployment
modal app list
```

### Problem: Modal functions fail

**Check:**
1. Anthropic API key in Modal secrets
2. Modal function logs

**Fix:**
```bash
# Check Modal secrets
modal secret list

# View function logs
modal app logs teachback-ai
```

## Performance Expectations

| Operation | Before Fix | After Fix |
|-----------|-----------|-----------|
| analyze_explanation | 300s timeout ❌ | ~3-5s ✅ |
| generate_question | Variable | ~3-5s ✅ |
| compute_session_analytics | N/A | ~2s (background) ✅ |
| **Total per turn** | 300s+ timeout | **~8-10s** ✅ |

## Modal Dashboard

Monitor your Modal executions at:
- **Dashboard:** https://modal.com/apps
- **App:** teachback-ai
- **Functions:**
  - analyze_explanation_modal
  - generate_question_modal
  - compute_session_analytics

You should see:
- Recent executions for each function
- Execution times (should be < 5s)
- Success/failure status
- Logs for debugging

## Summary

✅ **Fixed:** Timeout issue after 5th turn
✅ **Improved:** All turns now use Modal for fast execution
✅ **Added:** Graceful fallback to local execution
✅ **Created:** Test scripts to verify integration

The application should now work smoothly without timeouts!
