# Modal Integration for TeachBack AI

This document describes the Modal integration for TeachBack AI, which enables parallel cloud execution and background analytics processing.

## Overview

Modal integration provides:
- ⚡ **Parallel Processing**: Analyze explanations and generate questions simultaneously
- 📊 **Background Analytics**: Non-blocking session analytics computation
- 🚀 **Scalability**: Automatic scaling based on demand
- ☁️ **Cloud Execution**: Offload compute-intensive tasks to Modal cloud

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      TeachBack AI App                        │
│                   (Gradio + FastAPI)                         │
└────────────┬───────────────────────────┬────────────────────┘
             │                           │
             │ USE_MODAL=false           │ USE_MODAL=true
             │ (Local)                   │ (Modal Cloud)
             ▼                           ▼
    ┌────────────────┐         ┌─────────────────────────┐
    │    Sequential  │         │   Parallel Execution    │
    │    Execution   │         │   via Modal Functions   │
    │                │         │                         │
    │ 1. Analyze     │         │ 1. Analyze + Question   │
    │ 2. Question    │         │    (Parallel)           │
    │                │         │ 2. Background Analytics │
    │ Time: ~4-6s    │         │                         │
    └────────────────┘         │ Time: ~2-3s             │
                               └─────────────────────────┘
```

## File Structure

```
teachback-ai/
├── modal_setup.py                          # Modal app configuration
├── deploy_modal.py                         # Deployment script
├── test_modal_integration.py               # Test suite
├── src/
│   ├── modal_functions/
│   │   ├── __init__.py
│   │   ├── parallel_teaching.py            # Parallel analysis & questions
│   │   └── background_analytics.py         # Analytics computation
│   └── agents/
│       └── teaching_agent.py               # Updated with Modal support
└── .env                                    # USE_MODAL=true/false
```

## Setup Instructions

### 1. Install Modal

```bash
pip install modal>=0.63.0
```

### 2. Authenticate with Modal

```bash
modal token new
```

This opens your browser to authenticate with Modal.

### 3. Create Secrets in Modal

Create the required secrets in Modal:

```bash
# Required: Anthropic API key
modal secret create anthropic-api-key ANTHROPIC_API_KEY=sk-ant-...

# Optional: ElevenLabs API key (for voice features)
modal secret create elevenlabs-api-key ELEVENLABS_API_KEY=...
```

Alternatively, use the Modal dashboard at [modal.com](https://modal.com) to create secrets.

### 4. Deploy Modal Functions

```bash
python deploy_modal.py
```

This deploys all Modal functions to the cloud. You'll see output like:

```
🚀 TeachBack AI Modal Deployment
================================================================
📦 Deployed Functions:
  1. analyze_explanation_modal
  2. generate_question_modal
  3. parallel_analyze_and_question
  4. compute_session_analytics
  5. batch_analyze_sessions
================================================================
```

### 5. Enable Modal in Your App

Update your `.env` file:

```bash
USE_MODAL=true
```

### 6. Restart the Application

```bash
python app.py
```

You should see:
```
⚡ Powered by Modal — Parallel Execution Enabled
```

## Functions

### 1. `analyze_explanation_modal`

Analyzes user explanations using Claude API.

**Input:**
- `explanation`: User's explanation text
- `topic`: Topic being taught

**Output:**
- `confidence_score`: 0-1
- `clarity_score`: 0-1
- `knowledge_gaps`: List of gaps
- `unexplained_jargon`: List of terms
- `strengths`: List of strong points

**Usage:**
```python
from src.modal_functions.parallel_teaching import analyze_explanation_modal

analysis = analyze_explanation_modal.remote(
    explanation="Recursion is when a function calls itself",
    topic="Python Recursion"
)
```

### 2. `generate_question_modal`

Generates AI student questions based on analysis.

**Input:**
- `explanation`: User's explanation
- `mode`: AI student mode
- `analysis`: Analysis results
- `topic`: Topic being taught
- `conversation_history`: Previous turns

**Output:**
- Question string

**Usage:**
```python
from src.modal_functions.parallel_teaching import generate_question_modal

question = generate_question_modal.remote(
    explanation="...",
    mode="socratic",
    analysis=analysis,
    topic="Python Recursion",
    conversation_history=[]
)
```

### 3. `parallel_analyze_and_question`

Runs analysis and question generation in parallel.

**Input:**
- `explanation`: User's explanation
- `mode`: AI student mode
- `topic`: Topic being taught
- `conversation_history`: Previous turns (optional)

**Output:**
- `(analysis, question)`: Tuple of results

**Usage:**
```python
from src.modal_functions.parallel_teaching import parallel_analyze_and_question

analysis, question = parallel_analyze_and_question.remote(
    explanation="...",
    mode="socratic",
    topic="Python Recursion",
    conversation_history=[]
)
```

### 4. `compute_session_analytics`

Computes comprehensive session analytics.

**Resources:** 2 CPUs, 4GB memory, 300s timeout

**Input:**
- `session_history`: Dict with analyses and conversation

**Output:**
- `learning_curve`: List of clarity scores
- `clarity_trend`: "improving"/"stable"/"declining"
- `confidence_over_time`: List of confidence scores
- `persistent_gaps`: Repeated knowledge gaps
- `suggested_review_topics`: Topics needing review
- `total_turns`: Number of turns
- `average_confidence`: Mean confidence
- `average_clarity`: Mean clarity

**Usage (non-blocking):**
```python
from src.modal_functions.background_analytics import compute_session_analytics

# Spawn background task
call = compute_session_analytics.spawn(session_history)

# Continue with other work...

# Later, get results
analytics = call.get()
```

### 5. `batch_analyze_sessions`

Batch processes multiple sessions in parallel.

**Input:**
- `sessions`: List of session history dicts

**Output:**
- List of analytics results

**Usage:**
```python
from src.modal_functions.background_analytics import batch_analyze_sessions

sessions = [session1, session2, session3]
results = list(batch_analyze_sessions.map(sessions))
```

## Performance Comparison

### Sequential Execution (Local)
```
┌─────────────────────────────────┐
│  Analyze (2-3s)                 │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  Generate Question (2-3s)       │
└─────────────────────────────────┘

Total: ~4-6 seconds
```

### Parallel Execution (Modal)
```
┌─────────────────────────────────┐
│  Analyze (2-3s)                 │
└─────────────────────────────────┘
               │
┌──────────────┴──────────────────┐
│  Generate Question (2-3s)       │
└─────────────────────────────────┘

Total: ~2-3 seconds (50% faster)
```

## Testing

Run the test suite:

```bash
python -m unittest test_modal_integration.py -v
```

This tests:
- ✅ Modal availability
- ✅ Fallback behavior (USE_MODAL=false)
- ✅ Parallel execution performance
- ✅ Background analytics
- ✅ Batch session processing
- ✅ Import structure

## Fallback Behavior

The system gracefully falls back to local execution if:
- Modal is not installed
- `USE_MODAL=false` in environment
- Modal deployment is unavailable
- Modal execution fails

**Example:**
```python
from src.agents.teaching_agent import TeachingAgent

agent = TeachingAgent()

# If Modal is available and USE_MODAL=true:
analysis, question, time = agent.analyze_and_question_parallel(session_id, explanation)

# Otherwise, falls back to:
analysis = agent.analyze_explanation(session_id, explanation)
question = agent.generate_question(session_id, explanation, analysis, mode)
```

## Cost Optimization

Modal charges based on:
- **Compute time**: CPU/GPU seconds
- **Memory**: GB-seconds
- **Storage**: GB-months

Tips to optimize costs:
1. Use appropriate container sizes (default functions use minimal resources)
2. Leverage cold start caching (functions warm up after first use)
3. Use `.spawn()` for background tasks instead of blocking with `.remote()`
4. Monitor usage in Modal dashboard

**Free Tier:** Modal provides generous free credits for development.

## Troubleshooting

### Modal not found
```bash
pip install modal>=0.63.0
```

### Authentication failed
```bash
modal token new
```

### Secrets not found
```bash
modal secret list
modal secret create anthropic-api-key ANTHROPIC_API_KEY=...
```

### Deployment failed
- Check Modal dashboard for deployment status
- Verify all imports in `modal_setup.py`
- Ensure secrets are created correctly

### Functions not executing
- Verify `USE_MODAL=true` in `.env`
- Check Modal dashboard for function calls
- Review logs: `modal app logs teachback-ai`

### Cold start latency
- First call takes 2-5 seconds (image build)
- Subsequent calls are <500ms
- Modal automatically keeps functions warm based on usage

## Monitoring

View function calls and logs:

```bash
# View all apps
modal app list

# View function logs
modal app logs teachback-ai

# View function call history
modal app show teachback-ai
```

## Deployment to Production

For Hugging Face Spaces or other platforms:

1. **Keep Modal optional:**
   - Modal is already set up as optional dependency
   - App works without Modal (fallback to local)

2. **Set environment variables:**
   ```bash
   USE_MODAL=true  # Only if Modal is deployed
   ```

3. **Consider hybrid approach:**
   - Use Modal for compute-intensive tasks
   - Use local execution for simple operations

## Future Enhancements

Potential improvements:
- [ ] GPU support for faster Claude API calls
- [ ] Distributed tracing and monitoring
- [ ] Advanced caching strategies
- [ ] Multi-region deployment
- [ ] Custom autoscaling policies

## Support

- Modal Documentation: https://modal.com/docs
- TeachBack AI Issues: https://github.com/your-repo/issues
- Modal Community: https://modal.com/slack

## License

Same as TeachBack AI main license.
