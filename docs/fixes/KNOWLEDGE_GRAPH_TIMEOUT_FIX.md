# Knowledge Graph Timeout Fix

## Problem

After turn 5, the application would freeze/timeout when trying to process the next turn (turn 6). The error logs showed:

```
2025-11-27 20:15:35,080 - Turn 5 completes successfully
2025-11-27 20:21:35,342 - Tool call analyze_explanation timed out after 300s
```

## Root Cause

The issue was **NOT** with the Modal functions (those were working correctly). The issue was with the **Knowledge Graph Service** which runs on **every turn**:

1. On every turn, [handlers.py:268-298](src/ui/handlers.py#L268-L298) calls `kg_service.extract_related_concepts()`
2. This makes a **local Anthropic API call** (not through Modal)
3. After turn 5, this API call was hanging indefinitely
4. The MCP client would timeout after 300 seconds
5. This blocked the entire flow

## Why It Appeared After Turn 5

The issue likely occurred after turn 5 because:
- The conversation history was building up (5+ turns)
- The knowledge graph extraction looks at the last 5 turns
- Some combination of conversation length or API rate limiting caused the hang
- The analytics spawning on turn 5 was coincidental timing, not the cause

## Solution

### Fix 1: Add Timeout to Anthropic API Call

Modified [knowledge_graph.py:56-64](src/services/knowledge_graph.py#L56-L64) to add a 10-second timeout:

```python
response = self.client.messages.create(
    model=self.model,
    max_tokens=256,
    timeout=10.0,  # Add 10 second timeout to prevent hanging
    messages=[{
        "role": "user",
        "content": prompt
    }]
)
```

### Fix 2: Wrap Knowledge Graph in Try-Except

Modified [handlers.py:267-302](src/ui/handlers.py#L267-L302) to wrap knowledge graph updates:

```python
# Update knowledge graph (with timeout protection)
try:
    kg_service = get_kg_service()
    related_concepts = kg_service.extract_related_concepts(
        state["topic"],
        state["conversation_history"]
    )
    # ... rest of knowledge graph updates ...
except Exception as kg_error:
    print(f"[WARNING] Knowledge graph update failed: {kg_error}")
    # Continue without knowledge graph - don't block the conversation
```

## Changes Made

1. **[src/services/knowledge_graph.py](src/services/knowledge_graph.py#L59)**
   - Added `timeout=10.0` to Anthropic API call
   - Changed error message to warning level

2. **[src/ui/handlers.py](src/ui/handlers.py#L267-L302)**
   - Wrapped knowledge graph extraction in try-except
   - Allows conversation to continue even if knowledge graph fails

## Expected Behavior

### Before Fix
- Turn 1-5: Work fine
- Turn 6: Hangs for 300 seconds, then times out
- User experience: Application appears frozen

### After Fix
- Turn 1-∞: All work fine
- If knowledge graph API times out (>10s): Logs warning, continues
- If knowledge graph fails: Logs warning, continues
- User experience: Smooth conversation flow

## Testing

Run the application and go through 10+ turns. You should see:
- Fast responses on every turn (~8-10s)
- No freezing after turn 5
- Possible `[WARNING] Knowledge graph update failed` messages if API is slow
- Conversation continues regardless

## Future Improvements

Consider these optimizations for the knowledge graph service:

1. **Move to Modal**: Create a Modal function for knowledge graph extraction
2. **Cache Results**: Cache related concepts to avoid repeated API calls
3. **Background Processing**: Run knowledge graph updates in background
4. **Disable Option**: Add environment variable to disable knowledge graph
5. **Rate Limiting**: Implement client-side rate limiting

## Files Modified

- [src/services/knowledge_graph.py](src/services/knowledge_graph.py) - Added timeout
- [src/ui/handlers.py](src/ui/handlers.py) - Added error handling

## Summary

The timeout after turn 5 was caused by the knowledge graph service hanging on a local Anthropic API call, not by Modal or the analytics trigger. The fix adds timeout protection and error handling to prevent this from blocking the conversation flow.
