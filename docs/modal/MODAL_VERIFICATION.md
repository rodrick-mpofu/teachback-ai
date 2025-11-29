# Modal Integration Verification Guide

## ✅ Fixes Applied

### Issue
The error "Failed to spawn analytics task: Function has not been hydrated" occurred because:
1. Modal functions weren't properly deployed
2. The app was creating new TeachingAgent instances instead of using deployed functions
3. Module import errors in deployed functions

### Solution
1. **Created unified Modal app** - All functions in `modal_app.py`
2. **Fixed function lookups** - Using `modal.Function.from_name()` correctly
3. **Updated handlers** - Directly importing and calling deployed Modal functions
4. **Added state tracking** - Tracking all analyses for background analytics

---

## 🧪 Testing

### Test 1: Connection Test
```bash
python test_modal_connection.py
```

**Expected Output:**
```
[OK] Modal Token ID found: ak-L0TVyfO...
[OK] Modal package imported successfully (version 1.2.4)
[OK] Found compute_session_analytics
[OK] Found parallel_analyze_and_question
[OK] Function invocation successful!
```

### Test 2: Analytics Trigger Test
```bash
python test_analytics_trigger.py
```

**Expected Output:**
```
[OK] Task spawned successfully!
     Call ID: fc-01K...
[OK] Task completed successfully!
     - Total turns: 3
     - Average confidence: 0.78
     - Clarity trend: improving
```

---

## 🚀 Running Your App

### 1. Verify Environment Variables
Check your `.env` file has:
```bash
USE_MODAL=true
MODAL_TOKEN_ID=ak-...
MODAL_TOKEN_SECRET=as-...
ANTHROPIC_API_KEY=sk-ant-...
```

### 2. Start the App
```bash
python app.py
```

### 3. Expected Console Output on Startup
```
[OK] Connected to deployed Modal functions
✅ MCP Client initialized successfully
Running on local URL:  http://0.0.0.0:7860
```

### 4. During Teaching Session (Every 5th Turn)
When you reach the 5th interaction, you should see:
```
[ANALYTICS] Triggering background analytics computation (turn 5)...
[ANALYTICS] Session data: 5 analyses
[ANALYTICS] Analytics task spawned (call_id: fc-01K...)
```

---

## 📊 Verifying Modal Dashboard

### Check Modal Dashboard
1. Go to: https://modal.com/apps
2. Click on your `teachback-ai` app
3. You should see:
   - **Functions**: 5 deployed functions
   - **Recent calls**: Activity when you trigger analytics
   - **Logs**: Function execution logs

### Expected Functions
✅ `analyze_explanation_modal`
✅ `generate_question_modal`
✅ `parallel_analyze_and_question`
✅ `compute_session_analytics` ← This is what triggers on 5th turn
✅ `batch_analyze_sessions`

### Check Logs
After triggering analytics (5th interaction), click on `compute_session_analytics` in the dashboard to see:
- Execution time
- Input parameters (session data)
- Output (analytics results)
- Any errors (should be none)

---

## 🔍 Debugging

### If Modal Functions Don't Trigger

**1. Check Modal is enabled:**
```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('USE_MODAL:', os.getenv('USE_MODAL'))"
```
Should print: `USE_MODAL: true`

**2. Check Modal connection:**
```bash
python -c "from src.agents.teaching_agent import MODAL_AVAILABLE; print('Modal Available:', MODAL_AVAILABLE)"
```
Should print: `Modal Available: True`

**3. Check function reference:**
```bash
python -c "from src.agents.teaching_agent import compute_session_analytics; print(compute_session_analytics)"
```
Should print: `modal.Function.from_name('teachback-ai', 'compute_session_analytics')`

### If No Logs Appear in Modal Dashboard

**Possible causes:**
1. ❌ Modal functions not actually being called
   - **Check:** Console output when reaching 5th turn
   - **Fix:** Look for `[ANALYTICS]` log messages

2. ❌ Function fails silently
   - **Check:** Console for `[WARNING]` messages
   - **Fix:** See error details in console output

3. ❌ Wrong environment
   - **Check:** Modal dashboard environment (should be "main")
   - **Fix:** Redeploy with `python deploy_modal.py`

---

## 📝 Code Changes Summary

### Files Modified
1. **`modal_app.py`** (NEW) - Unified Modal app with all functions
2. **`src/ui/handlers.py`** - Fixed analytics trigger to use deployed functions
3. **`src/ui/components.py`** - Added `all_analyses` to state
4. **`src/agents/teaching_agent.py`** - Fixed Modal function lookups
5. **`deploy_modal.py`** - Simplified deployment

### Key Changes in `handlers.py`
```python
# OLD (BROKEN):
from src.agents.teaching_agent import TeachingAgent
agent = TeachingAgent()
agent.trigger_background_analytics(...)

# NEW (WORKING):
from src.agents.teaching_agent import compute_session_analytics, MODAL_AVAILABLE
call = compute_session_analytics.spawn(session_data)
```

---

## ✅ Success Checklist

- [ ] `python test_modal_connection.py` passes
- [ ] `python test_analytics_trigger.py` passes
- [ ] App starts with `[OK] Connected to deployed Modal functions`
- [ ] 5 functions visible in Modal dashboard
- [ ] Console shows `[ANALYTICS]` messages on 5th turn
- [ ] Modal dashboard shows execution logs

---

## 🆘 Getting Help

If issues persist:
1. Check Modal dashboard: https://modal.com/apps
2. Look for errors in console output (especially `[WARNING]` messages)
3. Verify deployment: `python deploy_modal.py`
4. Check environment: `USE_MODAL=true` in `.env`

---

## 🎯 What to Expect

**Timeline:**
- **Turn 1-4**: Regular teaching interactions (no analytics)
- **Turn 5**: Background analytics triggers
  - Function spawns (non-blocking, ~50ms)
  - Computes in background (~2-5 seconds)
  - UI remains responsive
  - Logs appear in Modal dashboard

**Performance:**
- Analytics computation: 2-5 seconds (in background)
- No UI blocking
- Results available via Modal dashboard

**Cost:**
- Modal free tier: 30 CPU-hours/month
- Each analytics call: ~2-5 seconds = ~0.001-0.002 CPU-hours
- Estimated: ~500-1000 analytics calls per month on free tier
