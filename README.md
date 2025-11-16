---
title: TeachBack AI
emoji: 🎓
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 5.49.1
app_file: app.py
pinned: false
tags:
  - mcp-in-action-track-consumer
  - agents
  - teaching
  - learning
  - education
  - anthropic
  - elevenlabs
license: mit
---

# 🎓 TeachBack AI

**"Learn by Teaching, Not Faking"**

[![Hackathon](https://img.shields.io/badge/MCP%20Hackathon-2025-blue)](https://huggingface.co/MCP-1st-Birthday)
[![Track](https://img.shields.io/badge/Track-MCP%20in%20Action%20Consumer-purple)](https://huggingface.co/MCP-1st-Birthday)
[![Gradio](https://img.shields.io/badge/Gradio-5.49.1-orange)](https://gradio.app)

---

## 🎯 What is TeachBack AI?

TeachBack AI is an **agentic learning application** that forces you to truly understand concepts by teaching them to a challenging AI student. Unlike passive learning tools that let you consume content, TeachBack makes **you the teacher** - and the AI student won't let you fake it.

Research shows that **teaching is the most effective way to learn**. The Feynman Technique proves that if you can't explain something simply, you don't understand it. TeachBack AI automates this by giving you an AI student that:
- Asks probing questions
- Challenges your explanations  
- Exposes knowledge gaps
- Forces you to think deeper

Perfect for:
- 📚 Students preparing for exams
- 💼 Job seekers practicing technical interviews
- 🎓 Self-learners mastering new topics
- 👨‍🏫 Educators testing their own understanding

---

## ✨ Features

### 🎭 **Multiple AI Student Personalities**

Choose your challenge level:

- **🤔 Socratic Student**
  - Asks "why?" to help you discover gaps
  - Patient and thoughtful
  - Guides you toward deeper understanding

- **😈 Contrarian Student**  
  - Challenges every claim you make
  - Provides counterexamples
  - Plays devil's advocate to strengthen your arguments

- **👶 Five-Year-Old Student**
  - Asks "why?" until you can explain it simply
  - Takes everything literally
  - Forces clear, jargon-free explanations

- **😰 Anxious Student**
  - Worries about edge cases and failure scenarios
  - Asks "what if...?" constantly
  - Makes you think comprehensively about your topic

### 🎯 **Real-Time Analysis**

Get instant feedback on your teaching:
- **Confidence Score** - Detects hedging language ("I think", "maybe")
- **Clarity Score** - Measures how well-structured your explanation is
- **Knowledge Gap Detection** - Identifies concepts you avoided or explained poorly
- **Jargon Spotter** - Catches technical terms you didn't explain

### 🎤 **Voice Mode** ✅
- Enable voice responses with a single checkbox
- Hear AI student responses with personality-matched voices powered by ElevenLabs
- Each personality has a distinct voice character:
  - Socratic: Thoughtful, patient voice
  - Contrarian: Confident, challenging voice
  - Five-Year-Old: Young, curious voice
  - Anxious: Nervous, worried voice
- Practice for real presentations and interviews with audio feedback

### 📊 **Progress Tracking**
- Session analytics and improvement metrics
- Learning curves over time
- Knowledge graphs showing concept mastery
- Spaced repetition reminders

---

## 🎬 Demo Video

> 📹 **[Demo Video Link]** *(Will be added by Nov 30)*

Watch TeachBack AI in action as a user attempts to teach recursion to the Contrarian Student!

---

## 🚀 How to Use

### 1️⃣ **Choose Your Topic**
Enter what you're learning: "Recursion in Python", "Photosynthesis", "Blockchain", etc.

### 2️⃣ **Select AI Student Mode**
Pick the personality that matches your challenge level.

### 3️⃣ **Start Teaching**
Explain the concept as best as you can, like you're teaching a real student.

### 4️⃣ **Answer Questions**
The AI student will ask questions to expose gaps in your understanding.

### 5️⃣ **Keep Going**
Continue teaching and refining your explanations until you truly understand!

### 6️⃣ **Review Your Progress**
Check your confidence scores, clarity ratings, and knowledge gaps.

---

## 🏗️ Tech Stack

### **AI & Agents**
- **🧠 Anthropic Claude** (via MCP) - Powers the teaching agent logic
- **🎤 ElevenLabs** - Natural voice synthesis for AI student personalities
- **🔧 Model Context Protocol (MCP)** - Agent tool orchestration
- **⚡ Blaxel** - Agent runtime and parallel task execution

### **Frontend**
- **🎨 Gradio 5** - Interactive web interface
- **📊 Real-time Analytics** - Live feedback visualization

### **Infrastructure**
- **☁️ Modal** - Background processing and compute
- **🤗 Hugging Face Spaces** - Deployment platform

---

## 🎓 The Science Behind It

TeachBack AI is based on proven learning techniques:

### **The Feynman Technique**
Named after physicist Richard Feynman, this method has four steps:
1. Choose a concept
2. Teach it to someone (or something) else
3. Identify gaps in your explanation
4. Review and simplify

TeachBack AI automates steps 2-4 with an AI that won't let you skip over the hard parts.

### **Active Recall**
Teaching requires you to actively retrieve information from memory, which is **3x more effective** than passive review.

### **The Protégé Effect**
Studies show that students who teach others learn material better than those who only study for themselves.

---

## 🛠️ Installation & Development

### **Run Locally**
```bash
# Clone the repository
git clone https://huggingface.co/spaces/R-odrick/teachback-ai
cd teachback-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Add your API keys to .env

# Run the app
python app.py
```

### **Environment Variables**

Create a `.env` file with:
```
ANTHROPIC_API_KEY=your_anthropic_key
ELEVENLABS_API_KEY=your_elevenlabs_key  # Optional - for voice mode
```

**For Hugging Face Spaces deployment:**
- Add API keys in Space Settings → Repository secrets
- `ANTHROPIC_API_KEY` is required for AI functionality
- `ELEVENLABS_API_KEY` is optional (app works without voice if not provided)

---

## 📁 Project Structure
```
teachback-ai/
├── app.py                          # Main Gradio application
├── src/
│   └── utils/                      # Utility functions
│       ├── claude_client.py        # Claude API integration
│       ├── elevenlabs_client.py    # ElevenLabs voice integration
│       └── __init__.py
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment template
├── .gitignore                      # Git ignore file
├── check_models.py                 # Utility to test available Claude models
└── README.md                       # This file
```

**Key Files:**
- `app.py` - Complete Gradio UI with all components and event handlers
- `src/utils/claude_client.py` - AI student personality prompts and Claude API calls
- `src/utils/elevenlabs_client.py` - Voice generation with personality-matched voices
- `requirements.txt` - All Python dependencies for deployment

---

## 🎯 Development Status

### ✅ **Phase 1: MVP** (COMPLETED)
- [x] Beautiful Gradio UI with sidebar layout
- [x] Text-based teaching interface
- [x] Multiple AI student personalities (4 unique modes)
- [x] Real-time analysis feedback (confidence & clarity scores)
- [x] Anthropic Claude 3 Opus integration
- [x] Knowledge gap detection with AI analysis
- [x] Session state management for multi-user support

### ✅ **Phase 2: Voice Integration** (COMPLETED)
- [x] Voice output with ElevenLabs integration
- [x] Personality-matched voices for each AI student
- [x] One-click voice mode toggle
- [x] Autoplay audio responses
- [ ] Voice input (speak explanations) - Future enhancement

### 🔮 **Phase 3: Advanced Features** (Future)
- [ ] Session persistence and history
- [ ] Progress tracking across sessions
- [ ] Knowledge graph visualization
- [ ] Spaced repetition system
- [ ] Multi-user leaderboards
- [ ] Export to flashcards (Anki)
- [ ] MCP server for tool orchestration

---

## 🚀 Deploying to Hugging Face Spaces

### Quick Deploy
1. Create a new Space on [Hugging Face](https://huggingface.co/spaces)
2. Choose **Gradio** as the SDK
3. Connect your GitHub repository or upload files
4. Add secrets in Space Settings → Repository secrets:
   - `ANTHROPIC_API_KEY` (required)
   - `ELEVENLABS_API_KEY` (optional for voice)
5. The app will auto-deploy using `app.py` and `requirements.txt`

### Important Notes
- **Model**: Uses `claude-3-opus-20240229` - ensure your API key has access
- **Port**: Configured for port 7860 (Gradio default)
- **Voice**: Works without ElevenLabs key, just disables voice mode
- **State Management**: Uses `gr.State()` for proper multi-user support

---

## 🌐 Social Media

📱 **Follow the development:**
- **LinkedIn:** [Rodrick Mpofu](https://www.linkedin.com/in/rodrick-mpofu/) - [Link to project post]
- **GitHub:** [Github](https://github.com/rodrick-mpofu)

🔗 **Share this project:**
```
🎓 Just discovered TeachBack AI - learn by teaching an AI that won't let you fake it!

Try it: [Your HF Space URL]

#MCPHackathon #AgenticAI #LearningByTeaching
```

---

## 🏆 Built For

**MCP's 1st Birthday Hackathon**  
November 14-30, 2025  
Hosted by Anthropic & Gradio

**Track:** MCP in Action - Consumer Applications  
**Tag:** `mcp-in-action-track-consumer`

---

## 🤝 Contributing

This project was built during the MCP Hackathon. Contributions, issues, and feature requests are welcome after the hackathon period!

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- **Anthropic** - For Claude API and MCP protocol
- **Gradio** - For the amazing UI framework
- **ElevenLabs** - For natural voice synthesis
- **Hugging Face** - For hosting infrastructure
- **MCP Hackathon** - For the opportunity and API credits

---

## 👨‍💻 Author

**Rodrick** - Data Science Graduate | Software Engineering Resident  
- LinkedIn: [Rodrick Mpofu](https://www.linkedin.com/in/rodrick-mpofu/)
- GitHub: [Github](https://github.com/rodrick-mpofu)

---

## 📊 Stats

![Space Badge](https://img.shields.io/badge/dynamic/json?url=https://huggingface.co/api/spaces/YOUR_USERNAME/teachback-ai&query=$.likes&label=Likes&color=blue)
![Status](https://img.shields.io/badge/Status-In%20Development-yellow)

---

**⭐ If you find this project helpful, please star it on Hugging Face!**

*Learn by teaching. Understand by explaining. Master by doing.*
