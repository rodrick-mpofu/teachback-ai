# MCP Setup Guide for TeachBack AI

This guide explains how to use the TeachBack AI MCP (Model Context Protocol) server in different scenarios.

## Table of Contents
- [Quick Start](#quick-start)
- [Using with Gradio App (Automatic)](#using-with-gradio-app-automatic)
- [Using with Claude Desktop](#using-with-claude-desktop)
- [Using with Cursor IDE](#using-with-cursor-ide)
- [Testing MCP Tools Directly](#testing-mcp-tools-directly)
- [Architecture Overview](#architecture-overview)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### Prerequisites

1. **Python 3.9+** installed
2. **ANTHROPIC_API_KEY** environment variable set
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file:

```bash
ANTHROPIC_API_KEY=your_api_key_here
```

---

## Using with Gradio App (Automatic)

**No manual MCP setup needed!** The Gradio app automatically manages the MCP server.

### How It Works

When you run the Gradio app:

```bash
python app.py
```

The app automatically:
1. ✅ Initializes the MCP client wrapper
2. ✅ Starts the MCP server as a subprocess
3. ✅ Connects via stdio protocol
4. ✅ Cleans up when you close the app

### What You'll See

```
✅ MCP Client initialized successfully
Running on local URL:  http://0.0.0.0:7860
```

In the UI:
- **Sidebar**: 🟢 **MCP Connected** - Using MCP Server for AI
- **Footer**: 🟢 MCP Server Active

### Session Flow

1. **Start a session** → MCP creates session with AI student personality
2. **Submit explanation** → MCP analyzes your explanation (confidence, clarity, gaps)
3. **Get question** → MCP generates personalized question based on analysis
4. **View progress** → Enhanced analysis panel shows gaps, jargon, and strengths

**That's it!** Just use the app normally - MCP runs in the background.

---

## Using with Claude Desktop

You can also use the MCP server directly with Claude Desktop for a conversational teaching experience.

### Step 1: Locate Your MCP Server

Find the full path to `mcp_server.py`:

```bash
# On Windows
cd c:\Users\rodri\repos\teachback-ai
echo %CD%\mcp_server.py

# On macOS/Linux
cd /path/to/teachback-ai
echo $(pwd)/mcp_server.py
```

### Step 2: Configure Claude Desktop

1. **Open Claude Desktop settings**
2. **Navigate to**: Developer → Model Context Protocol
3. **Add a new MCP server** with this configuration:

```json
{
  "mcpServers": {
    "teachback-ai": {
      "command": "python",
      "args": [
        "C:\\Users\\rodri\\repos\\teachback-ai\\mcp_server.py"
      ],
      "env": {
        "ANTHROPIC_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

**Note**: Replace the path with your actual path from Step 1.

#### macOS/Linux Configuration

```json
{
  "mcpServers": {
    "teachback-ai": {
      "command": "python3",
      "args": [
        "/Users/yourname/path/to/teachback-ai/mcp_server.py"
      ],
      "env": {
        "ANTHROPIC_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### Step 3: Restart Claude Desktop

After saving the configuration, restart Claude Desktop to load the MCP server.

### Step 4: Use TeachBack Tools

In Claude Desktop, you can now use the teaching tools:

#### Example Conversation

**You:**
> Use the create_teaching_session tool to start a session on "Python recursion" with the socratic student mode.

**Claude:**
```
I'll create a teaching session for you.

[Uses create_teaching_session tool]

Great! Your session is ready. The Socratic student says:
"I'm interested in learning about Python recursion. What's the core idea behind it, and why should I care?"

Go ahead and explain recursion!
```

**You:**
> Recursion is when a function calls itself to solve a problem.

**Claude:**
```
[Uses analyze_explanation tool]

Let me analyze that...

Analysis shows:
- Confidence: 0.6
- Clarity: 0.5
- Knowledge gaps: ["No explanation of base case", "Missing why recursion is useful"]

[Uses generate_question tool]

The student asks: "That's a start, but why would a function call itself? Doesn't that create an infinite loop? How does it know when to stop?"
```

---

## Using with Cursor IDE

Cursor IDE also supports MCP servers!

### Configuration for Cursor

1. **Open Cursor Settings** → **MCP Servers**
2. **Add configuration**:

```json
{
  "teachback-ai": {
    "command": "python",
    "args": ["C:\\path\\to\\teachback-ai\\mcp_server.py"],
    "env": {
      "ANTHROPIC_API_KEY": "your_api_key_here"
    }
  }
}
```

3. **Restart Cursor**

### Using in Cursor

The AI assistant in Cursor can now:
- Create teaching sessions
- Analyze your explanations
- Generate follow-up questions
- Track your learning progress

---

## Testing MCP Tools Directly

You can test the MCP server without any client:

### Method 1: Python Script

Create `test_mcp.py`:

```python
import asyncio
from src.mcp.client_wrapper import MCPClientWrapper

async def test_session():
    # Initialize client
    client = MCPClientWrapper()

    # Create session
    session = client.create_teaching_session(
        user_id="test_user",
        topic="Binary Search",
        mode="socratic"
    )
    print("Session created:", session)

    # Analyze explanation
    analysis = client.analyze_explanation(
        session_id=session["session_id"],
        explanation="Binary search divides the array in half each time."
    )
    print("Analysis:", analysis)

    # Generate question
    question = client.generate_question(
        session_id=session["session_id"],
        explanation="Binary search divides the array in half each time.",
        analysis=analysis,
        mode="socratic"
    )
    print("Question:", question)

    # Get summary
    summary = client.get_session_summary(session["session_id"])
    print("Summary:", summary)

    # Cleanup
    client.cleanup()

if __name__ == "__main__":
    asyncio.run(test_session())
```

Run it:

```bash
python test_mcp.py
```

### Method 2: Interactive Python

```python
from src.mcp.client_wrapper import MCPClientWrapper

# Start client
client = MCPClientWrapper()

# Create session
result = client.create_teaching_session("user1", "Recursion", "socratic")
print(result)

# Use the session_id for next calls
session_id = result["session_id"]

# Continue testing...
client.cleanup()
```

---

## Architecture Overview

### How MCP Powers TeachBack AI

```
┌─────────────────────────────────────────────────────────────────┐
│                         Gradio Web App                           │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  User Interface (Topic, Mode, Explanation Input)           │ │
│  └───────────────────────┬────────────────────────────────────┘ │
│                          │                                       │
│  ┌───────────────────────▼────────────────────────────────────┐ │
│  │           MCPClientWrapper (Sync Interface)                │ │
│  │  • Manages event loop                                      │ │
│  │  • Converts async → sync for Gradio                        │ │
│  └───────────────────────┬────────────────────────────────────┘ │
└────────────────────────────┼───────────────────────────────────┘
                             │ stdio (stdin/stdout)
┌────────────────────────────▼───────────────────────────────────┐
│                    MCP Server (mcp_server.py)                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Tools:                                                  │   │
│  │  • create_teaching_session                              │   │
│  │  • analyze_explanation                                  │   │
│  │  • generate_question                                    │   │
│  │  • get_session_summary                                  │   │
│  └────────────────────┬─────────────────────────────────────┘   │
└─────────────────────────┼──────────────────────────────────────┘
                          │
┌─────────────────────────▼──────────────────────────────────────┐
│              TeachingAgent (teaching_agent.py)                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Session Management (in-memory dictionary)               │  │
│  │  • Creates sessions with AI student personalities        │  │
│  │  • Stores conversation history                           │  │
│  │  • Tracks progress & analytics                           │  │
│  └────────────────────┬──────────────────────────────────────┘  │
└─────────────────────────┼──────────────────────────────────────┘
                          │ API calls
┌─────────────────────────▼──────────────────────────────────────┐
│                  Anthropic Claude API                           │
│               (claude-3-opus-20240229)                          │
│  • Analyzes explanations                                        │
│  • Detects knowledge gaps                                       │
│  • Generates personality-based questions                        │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow Example

1. **User** enters topic "Recursion" + mode "Socratic"
2. **Gradio** → `MCPClientWrapper.create_teaching_session()`
3. **MCP Client** → Calls MCP server tool via stdio
4. **MCP Server** → Routes to `TeachingAgent.create_session()`
5. **TeachingAgent** → Creates session, stores state
6. **MCP Server** → Returns `{session_id, welcome_message}`
7. **MCP Client** → Returns to Gradio
8. **Gradio** → Displays welcome message to user

### AI Student Personalities

```
┌──────────────────────────────────────────────────────────────┐
│                    Personality Modes                         │
├──────────────────────────────────────────────────────────────┤
│  🤔 Socratic Student                                         │
│     • Asks "why?" to expose deeper understanding             │
│     • Patient, guides toward first principles                │
│                                                              │
│  😈 Contrarian Student                                       │
│     • Challenges claims with counterexamples                 │
│     • Skeptical, plays devil's advocate                      │
│                                                              │
│  👶 Five-Year-Old Student                                    │
│     • Demands simple, jargon-free explanations               │
│     • Takes things literally, asks "why?" repeatedly         │
│                                                              │
│  😰 Anxious Student                                          │
│     • Worries about edge cases and failure scenarios         │
│     • Asks "what if...?" constantly                          │
└──────────────────────────────────────────────────────────────┘
```

---

## Troubleshooting

### Issue: "MCP Client initialization failed"

**Symptoms:**
```
⚠️ Failed to initialize MCP Client: ...
```

**Solutions:**

1. **Check ANTHROPIC_API_KEY**:
   ```bash
   # Windows
   echo %ANTHROPIC_API_KEY%

   # macOS/Linux
   echo $ANTHROPIC_API_KEY
   ```

2. **Verify dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Check Python version**:
   ```bash
   python --version  # Should be 3.9+
   ```

---

### Issue: "Could not locate mcp_server.py"

**Symptoms:**
```
RuntimeError: Could not locate mcp_server.py
```

**Solutions:**

1. **Verify file exists**:
   ```bash
   ls mcp_server.py  # Should exist in project root
   ```

2. **Run from project root**:
   ```bash
   cd /path/to/teachback-ai
   python app.py
   ```

---

### Issue: "Tool call timed out"

**Symptoms:**
```
TimeoutError: Tool call timed out after 30 seconds
```

**Solutions:**

1. **Increase timeout**:
   ```python
   # In app.py
   mcp_client = MCPClientWrapper(timeout=60)  # Increase to 60s
   ```

2. **Check API key quota**: Verify you haven't hit rate limits

3. **Test API directly**:
   ```python
   from anthropic import Anthropic
   client = Anthropic()
   response = client.messages.create(
       model="claude-3-opus-20240229",
       max_tokens=100,
       messages=[{"role": "user", "content": "Hello"}]
   )
   print(response)
   ```

---

### Issue: Claude Desktop doesn't show tools

**Solutions:**

1. **Check configuration path**: Ensure path to `mcp_server.py` is absolute
2. **Verify Python command**: Use `python3` on macOS/Linux
3. **Check logs**: Claude Desktop → Settings → Logs
4. **Test server manually**:
   ```bash
   python mcp_server.py
   # Should start without errors
   ```

---

### Issue: "Session not found" errors

**Symptoms:**
```
KeyError: Session abc-123 not found
```

**Solutions:**

1. **Sessions are in-memory**: Restarting the server clears sessions
2. **Always create session first**: Use `create_teaching_session` before other tools
3. **Check session_id**: Ensure you're using the correct session_id from creation

---

### Issue: Analysis returns empty results

**Solutions:**

1. **Provide detailed explanations**: Single sentences may not give enough context
2. **Check API response**: Look at console logs for Claude API errors
3. **Verify model access**: Ensure you have access to `claude-3-opus-20240229`

---

## Advanced Usage

### Custom User IDs

```python
client = MCPClientWrapper()

# Use unique user IDs for multi-user scenarios
session1 = client.create_teaching_session(
    user_id="alice@example.com",
    topic="Python",
    mode="socratic"
)

session2 = client.create_teaching_session(
    user_id="bob@example.com",
    topic="JavaScript",
    mode="contrarian"
)
```

### Session Persistence

Currently, sessions are stored in-memory. To persist sessions:

1. **Option A**: Modify `TeachingAgent` to use database storage
2. **Option B**: Export session summaries before server shutdown:

```python
# Get session summary before closing
summary = client.get_session_summary(session_id)

# Save to file
import json
with open(f"session_{session_id}.json", "w") as f:
    json.dump(summary, f, indent=2)
```

### Monitoring & Debugging

Enable verbose logging:

```python
import logging

# In mcp_server.py or app.py
logging.basicConfig(level=logging.DEBUG)
```

This will show:
- MCP tool calls
- Claude API requests/responses
- Session state changes
- Error tracebacks

---

## Next Steps

- ✅ **Run the Gradio app**: `python app.py`
- ✅ **Try different AI student modes**: Socratic, Contrarian, Five-Year-Old, Anxious
- ✅ **Configure Claude Desktop**: Add TeachBack AI as an MCP server
- ✅ **Experiment with topics**: Test your knowledge on any subject
- ✅ **Review session summaries**: Track your progress and persistent gaps

---

## Support

**Issues?** Open an issue on GitHub: [teachback-ai/issues](https://github.com/rodrick-mpofu/teachback-ai/issues)

**Questions?** Check the [README.md](README.md) for more information.

**Hackathon:** Built for MCP's 1st Birthday Hackathon 🎉

---

**Happy Teaching!** 🎓
