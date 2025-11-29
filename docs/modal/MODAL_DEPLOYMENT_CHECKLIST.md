# Modal Deployment Checklist

Use this checklist to deploy Modal integration for TeachBack AI.

## Pre-Deployment Checklist

- [ ] **Modal installed**: `pip install modal>=0.63.0`
- [ ] **Tests passing locally**: `python -m unittest test_modal_integration.py -v`
- [ ] **Anthropic API key ready**: Have your `sk-ant-...` key available
- [ ] **Environment variables**: `.env` file exists with `ANTHROPIC_API_KEY`

## Deployment Steps

### Step 1: Authenticate with Modal
```bash
modal token new
```
- [ ] Browser opened and you signed in
- [ ] Token saved successfully
- [ ] Message: "Token created and saved"

**Verification:**
```bash
modal profile current
# Should show your email/username
```

---

### Step 2: Create Secrets in Modal

#### Required Secret: Anthropic API Key
```bash
modal secret create anthropic-api-key ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```
- [ ] Secret created successfully
- [ ] No error messages

#### Optional Secret: ElevenLabs API Key
```bash
modal secret create elevenlabs-api-key ELEVENLABS_API_KEY=your-elevenlabs-key
```
- [ ] Secret created (or skipped if not using voice)

**Verification:**
```bash
modal secret list
# Should show:
# - anthropic-api-key
# - elevenlabs-api-key (if created)
```

---

### Step 3: Deploy Modal Functions
```bash
python deploy_modal.py
```

**Expected Output:**
```
🚀 Starting Modal deployment...
This may take a few minutes on first deployment...

✅ Deployment completed successfully!
================================================================
📦 Deployed Functions:
  1. analyze_explanation_modal
  2. generate_question_modal
  3. parallel_analyze_and_question
  4. compute_session_analytics
  5. batch_analyze_sessions
================================================================
```

- [ ] Deployment completed without errors
- [ ] All 5 functions listed
- [ ] No "failed" messages

**Verification:**
```bash
modal app list
# Should show: teachback-ai

modal app show teachback-ai
# Should show all 5 functions
```

---

### Step 4: Enable Modal in Application

Edit `.env` file:
```bash
USE_MODAL=true
```

- [ ] `.env` file updated
- [ ] `USE_MODAL=true` is set (not "false")

**Verification:**
```bash
cat .env | grep USE_MODAL
# Should show: USE_MODAL=true
```

---

### Step 5: Test Modal Integration
```bash
python -m unittest test_modal_integration.py -v
```

**Expected Results:**
- [ ] `test_modal_availability`: ✅ PASS
- [ ] `test_fallback_behavior`: ✅ PASS
- [ ] `test_modal_enabled_flag`: ✅ PASS
- [ ] `test_parallel_execution_performance`: ✅ PASS (not skipped)
- [ ] `test_background_analytics`: ✅ PASS
- [ ] `test_batch_session_processing`: ✅ PASS (not error)
- [ ] `test_trigger_background_analytics`: ✅ PASS
- [ ] `test_import_structure`: ✅ PASS

**All tests should PASS with no errors or skips**

---

### Step 6: Start Application
```bash
python app.py
```

**Expected in Console:**
- [ ] "✅ MCP Client initialized successfully"
- [ ] No Modal-related errors

**Expected in UI:**
- [ ] Page loads successfully
- [ ] Header shows: "⚡ Powered by Modal — Parallel Execution Enabled"
- [ ] Can start a teaching session
- [ ] Student questions appear normally

---

### Step 7: Verify Modal Execution

1. **Start a teaching session**
   - [ ] Session starts successfully

2. **Submit an explanation**
   - [ ] Response appears
   - [ ] Check console for: "⚡ Using Modal for parallel execution..."
   - [ ] Check console for: "✅ Modal execution completed in X.XXs"

3. **Submit 5 explanations**
   - [ ] After 5th explanation, see: "📊 Computing analytics in background..."
   - [ ] Check console for: "📊 Triggering background analytics computation..."

---

## Post-Deployment Verification

### Monitor Modal Dashboard
Visit: https://modal.com/apps

- [ ] App "teachback-ai" is listed
- [ ] Functions show "Active" status
- [ ] Recent function calls appear
- [ ] No errors in logs

### Check Function Logs
```bash
modal app logs teachback-ai
```
- [ ] Logs show function executions
- [ ] No error messages
- [ ] API calls succeeding

### Performance Comparison
```bash
# In Python
python -c "from test_modal_integration import run_performance_comparison; run_performance_comparison()"
```
- [ ] Modal execution faster than sequential
- [ ] Speedup > 1.0x
- [ ] No errors

---

## Troubleshooting

### Deployment Failed
**Error:** "No module named 'modal'"
```bash
pip install modal>=0.63.0
```

**Error:** "Not authenticated"
```bash
modal token new
```

**Error:** "Secret not found"
```bash
modal secret create anthropic-api-key ANTHROPIC_API_KEY=...
```

### Tests Still Skipping
**Issue:** Tests show "Modal not deployed"

**Solution:**
1. Verify deployment: `modal app list`
2. Check app status: `modal app show teachback-ai`
3. Re-deploy if needed: `python deploy_modal.py`

### Functions Not Executing
**Issue:** Console shows "⚠️ Modal execution failed"

**Solution:**
1. Check secrets: `modal secret list`
2. View logs: `modal app logs teachback-ai`
3. Verify `USE_MODAL=true` in `.env`

### Performance Not Improved
**Issue:** Modal not faster than sequential

**Possible Causes:**
- Cold start (first call is slower)
- Network latency
- API rate limits

**Solution:**
- Run multiple tests to warm up functions
- Check Modal dashboard for cold starts
- Verify network connectivity

---

## Rollback Plan

If something goes wrong, you can easily rollback:

### Option 1: Disable Modal (Keep Deployment)
```bash
# In .env file
USE_MODAL=false
```
App continues working with local execution.

### Option 2: Undeploy from Modal
```bash
modal app stop teachback-ai
```

### Option 3: Remove Modal Entirely
```bash
pip uninstall modal
```
App falls back to local execution automatically.

---

## Success Criteria

✅ **Deployment is successful when:**

1. All tests pass (no skips, no errors)
2. UI shows "⚡ Powered by Modal" indicator
3. Console shows Modal execution logs
4. Modal dashboard shows active functions
5. Response time improved (~50% faster)
6. Background analytics working (every 5th turn)

---

## Maintenance

### View Usage
```bash
modal app show teachback-ai
```

### Check Costs
Visit: https://modal.com/settings/billing

### Update Functions
After code changes:
```bash
python deploy_modal.py
```
(No need to recreate secrets)

### Monitor Performance
```bash
modal app logs teachback-ai --follow
```

---

## Support Resources

- **Modal Docs:** https://modal.com/docs
- **Modal Slack:** https://modal.com/slack
- **TeachBack AI Docs:** See MODAL_INTEGRATION.md
- **Test Suite:** `python -m unittest test_modal_integration.py -v`

---

**Status:** Ready to deploy! Follow the checklist step by step. ✅
