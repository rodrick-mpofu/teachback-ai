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

### 🎤 **Voice Mode** *(Coming Soon)*
- Speak your explanations naturally
- Hear AI student responses with personality-matched voices
- Practice for real presentations and interviews

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
ELEVENLABS_API_KEY=your_elevenlabs_key
OPENAI_API_KEY=your_openai_key
```

---

## 📁 Project Structure
```
teachback-ai/
├── app.py                 # Main Gradio application
├── src/
│   ├── agents/           # Teaching agent logic
│   │   └── teaching_agent.py
│   ├── mcp/              # MCP server implementation
│   │   └── teaching_mcp.py
│   ├── ui/               # UI components
│   │   └── gradio_interface.py
│   └── utils/            # Utility functions
│       └── analysis.py
├── requirements.txt      # Python dependencies
├── .env.example         # Environment template
└── README.md            # This file
```

---

## 🎯 Roadmap

### ✅ **Phase 1: MVP** (Current)
- [ ] Basic Gradio UI
- [ ] Text-based teaching interface
- [ ] Multiple AI student personalities
- [ ] Real-time analysis feedback
- [ ] MCP server integration
- [ ] Anthropic Claude integration

### 🚧 **Phase 2: Voice & Polish**
- [ ] Voice input (speak explanations)
- [ ] Voice output (AI student speaks)
- [ ] Personality-matched voices
- [ ] Session persistence

### 🔮 **Phase 3: Advanced Features**
- [ ] Progress tracking across sessions
- [ ] Knowledge graph visualization
- [ ] Spaced repetition system
- [ ] Multi-user leaderboards
- [ ] Export to flashcards (Anki)

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
