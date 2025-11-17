# TeachBack AI - Quick Start Guide

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   Create a `.env` file with:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ELEVENLABS_API_KEY=your_elevenlabs_key_here  # Optional for voice
   ```

3. **Run the app:**
   ```bash
   python app.py
   ```

4. **Open your browser:**
   Navigate to `http://localhost:7860`

---

## Using the New Features

### 1. Teaching Session (with Auto-Save)
1. Go to the **"🎓 Teach"** tab
2. Enter a topic (e.g., "Recursion in Python")
3. Choose an AI student mode
4. Click "Start Teaching Session"
5. **NEW:** Session is automatically saved to database!

### 2. View Your History
1. Click the **"📚 Session History"** tab
2. See all your past sessions
3. View your stats in the sidebar
4. Track your learning streak!

### 3. Track Your Progress
1. Click the **"📈 Progress Tracker"** tab
2. Adjust time range with the slider
3. See your confidence and clarity trends
4. Monitor your improvement over time

### 4. Explore Your Knowledge Graph
1. Click the **"🕸️ Knowledge Graph"** tab
2. See all topics you've taught
3. **Interact with the graph:**
   - Drag nodes to rearrange
   - Scroll to zoom
   - Hover to see details
   - Bigger nodes = taught more often
   - Color indicates confidence level

### 5. Use Spaced Repetition
1. Click the **"🔁 Review Schedule"** tab
2. See which topics are due for review
3. **To record a review:**
   - Expand "Record a Review"
   - Enter the Review Item ID
   - Rate your recall (0-5)
   - System calculates next review date!

---

## Tips for Success

### Get the Most Out of Each Feature:

**Session History:**
- Review past sessions to see your growth
- Identify patterns in your teaching
- Learn from your knowledge gaps

**Progress Tracking:**
- Aim for consistent daily practice
- Watch your confidence trend upward
- Celebrate your streaks!

**Knowledge Graph:**
- Use it to find connections between topics
- Identify areas you know well vs. areas to review
- Plan your learning path visually

**Spaced Repetition:**
- Review topics when they're due
- Be honest with your quality ratings
- Trust the algorithm - it works!

---

## First Session Walkthrough

### Step 1: Start Teaching
```
Topic: "Binary Search Algorithm"
Mode: "🤔 Socratic Student"
Voice: Optional (enable if you want)
```

### Step 2: Teach the Concept
The AI student asks: "What's the core idea behind binary search?"

You explain: "Binary search works by dividing a sorted array in half..."

### Step 3: Session Auto-Saves
- ✅ Conversation saved to database
- ✅ Your confidence/clarity analyzed
- ✅ Knowledge gaps identified
- ✅ Related concepts extracted
- ✅ Review item created

### Step 4: Explore Features
After completing the session:
1. Check **Session History** - See your session listed
2. Check **Progress Tracker** - See today's bar chart
3. Check **Knowledge Graph** - See "Binary Search" node
4. Check **Review Schedule** - Topic added for future review!

---

## What Happens Automatically

Every time you complete a teaching session:

1. **Database Storage:**
   - Session details saved
   - All conversations stored
   - Analysis results recorded

2. **Knowledge Graph:**
   - Topic node created/updated
   - Related concepts extracted by AI
   - Connections mapped

3. **Progress Tracking:**
   - Daily metrics updated
   - Streak calculated
   - Stats aggregated

4. **Spaced Repetition:**
   - Review item created
   - Initial interval set (1 day)
   - Quality calculated from performance

**You don't have to do anything - it all happens behind the scenes!**

---

## Understanding the Metrics

### Confidence Score (0-100%)
How certain you are in your explanations:
- **0-50%**: Uncertain, lots of "maybe", "I think"
- **50-75%**: Moderate confidence
- **75-100%**: Very confident, clear statements

### Clarity Score (0-100%)
How well-structured and clear your teaching is:
- **0-50%**: Confusing, disorganized
- **50-75%**: Decent structure
- **75-100%**: Crystal clear, well-organized

### Review Quality (0-5)
For spaced repetition reviews:
- **0**: Complete blackout
- **1**: Vague memory
- **2**: Incorrect but familiar
- **3**: Correct with difficulty *(passing)*
- **4**: Correct after brief thought
- **5**: Perfect recall

---

## Troubleshooting

### "No sessions found"
→ Complete at least one teaching session first

### "Knowledge graph is empty"
→ Teach some topics, then click refresh

### Database errors
→ Check that `teachback.db` isn't locked
→ Try restarting the app

### Features not showing
→ Make sure you're on the latest code
→ Check that SQLAlchemy is installed: `pip install sqlalchemy>=2.0.0`

---

## Data Location

All your data is stored in:
```
teachback.db (SQLite database in project root)
```

**To backup:**
```bash
cp teachback.db my_backup.db
```

**To reset (⚠️ deletes all data):**
```bash
rm teachback.db
# Will be recreated on next run
```

---

## Next Steps

1. ✅ Complete your first teaching session
2. ✅ Check out all 4 new tabs
3. ✅ Teach multiple topics to build your graph
4. ✅ Review topics when they're due
5. ✅ Track your progress daily
6. ✅ Read `FEATURES_GUIDE.md` for detailed docs

---

## Support

**Documentation:**
- `README.md` - Main project documentation
- `FEATURES_GUIDE.md` - Detailed feature documentation
- `IMPLEMENTATION_SUMMARY.md` - Technical details

**Issues:**
- GitHub Issues for bug reports
- Include error messages and steps to reproduce

---

## Have Fun Learning! 🎓

Remember: The best way to learn is to teach. These features help you:
- **Remember** what you've learned (spaced repetition)
- **Connect** ideas (knowledge graph)
- **Improve** over time (progress tracking)
- **Reflect** on your journey (session history)

Happy teaching! 🚀
