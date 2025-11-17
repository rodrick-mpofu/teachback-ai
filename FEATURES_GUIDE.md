# TeachBack AI - Advanced Features Guide

## Overview

TeachBack AI now includes four powerful features to enhance your learning journey:

1. **Session Persistence & History** - All your teaching sessions are automatically saved
2. **Progress Tracking** - Track your learning metrics over time
3. **Knowledge Graph Visualization** - See how your knowledge connects
4. **Spaced Repetition System** - Optimize long-term retention with SM-2 algorithm

---

## 1. Session Persistence & History

### What it does
Every teaching session is automatically saved to a local SQLite database, including:
- All conversations (your explanations and AI responses)
- Analysis results (confidence, clarity scores)
- Knowledge gaps identified
- Session metadata (date, mode, topic)

### How to use
1. Navigate to the **"📚 Session History"** tab
2. Click **"🔄 Refresh History"** to view your sessions
3. See your complete learning statistics in the sidebar

### Benefits
- Never lose your progress
- Review past sessions to see improvement
- Track which topics you've covered
- Monitor your learning streak

---

## 2. Progress Tracking

### What it does
Automatically aggregates your teaching performance into daily metrics:
- Sessions completed per day
- Average confidence and clarity scores
- Learning streaks
- Unique topics covered

### How to use
1. Navigate to the **"📈 Progress Tracker"** tab
2. Adjust the time range slider (7-90 days)
3. View your progress bars for each day

### Key Metrics
- **Confidence Score**: How certain you are in your explanations
- **Clarity Score**: How well-structured and clear your teaching is
- **Streak**: Consecutive days of completed sessions
- **Total Turns**: Number of teaching exchanges

---

## 3. Knowledge Graph Visualization

### What it does
Creates an interactive, visual representation of all topics you've taught and their relationships.

### Graph Features
- **Node Size**: Larger = taught more times
- **Node Color**:
  - 🟢 Green = High confidence (>75%)
  - 🟡 Yellow = Medium confidence (50-75%)
  - 🔵 Blue = Low confidence (<50%)
- **Edges**: Show relationships between topics
- **Interactive**: Drag nodes, zoom, hover for details

### How to use
1. Navigate to the **"🕸️ Knowledge Graph"** tab
2. Click **"🔄 Refresh Graph"** to update
3. Interact with the graph:
   - **Drag** nodes to rearrange
   - **Scroll** to zoom in/out
   - **Hover** over nodes to see details
   - **Click** nodes for more info

### AI-Powered Concept Extraction
The system uses Claude AI to automatically identify related concepts from your teaching sessions and create connections in the graph.

---

## 4. Spaced Repetition System

### What it does
Implements the **SM-2 algorithm** (used by Anki and SuperMemo) to schedule optimal review times for topics you've taught.

### How it works
1. After completing a teaching session, the topic is added to your review queue
2. Based on your performance (confidence, clarity, gaps), the system calculates:
   - **Easiness Factor (EF)**: How difficult the topic is for you
   - **Repetition Number**: How many times you've reviewed it
   - **Interval**: Days until next review (1, 6, then exponentially increasing)

### Review Quality Scores
When you review a topic, rate your recall:
- **5**: Perfect recall, no hesitation
- **4**: Correct after brief thought
- **3**: Correct with difficulty *(passing threshold)*
- **2**: Incorrect but familiar
- **1**: Vague memory
- **0**: Complete blank

### How to use
1. Navigate to the **"🔁 Review Schedule"** tab
2. See reviews that are due now (highlighted in yellow)
3. View upcoming reviews for the next 14 days
4. To record a review:
   - Expand **"✏️ Record a Review"**
   - Enter the Review Item ID (shown in the due list)
   - Rate your quality (0-5)
   - Click **"✅ Record Review"**

### Benefits
- **Optimize retention**: Review at the perfect time (not too early, not too late)
- **Save time**: Focus only on topics that need review
- **Long-term memory**: Build strong, lasting knowledge

---

## Database Structure

All data is stored in `teachback.db` (SQLite) with the following tables:

### Core Tables
- **users**: User profiles
- **sessions**: Teaching sessions
- **conversations**: Individual messages
- **analyses**: Performance analysis results

### Knowledge Management
- **knowledge_nodes**: Topics in your knowledge graph
- **knowledge_edges**: Relationships between topics

### Spaced Repetition
- **review_items**: Topics in review queue with SM-2 parameters

### Progress Tracking
- **progress_metrics**: Daily/weekly aggregated statistics

---

## Tips for Best Results

### For Better Progress Tracking
1. **Be consistent**: Try to teach daily to build streaks
2. **Diverse topics**: Cover a variety of subjects to expand your graph
3. **Complete sessions**: Finish all 10 turns for full analysis

### For Knowledge Graph
1. **Mention related concepts**: When explaining, naturally reference related ideas
2. **Teach prerequisites**: Build knowledge from foundations up
3. **Review the graph**: Use it to identify gaps in your understanding

### For Spaced Repetition
1. **Be honest**: Rate your recall accurately
2. **Review on time**: Don't skip reviews when they're due
3. **Re-teach**: Use the main teaching interface to review topics
4. **Quality 3+ passes**: Aim for at least "correct with difficulty"

### For Overall Learning
1. **Focus on clarity**: Clear teaching = clear understanding
2. **Address knowledge gaps**: Pay attention to identified gaps
3. **Track trends**: Watch your confidence/clarity over time
4. **Use all features together**: They complement each other!

---

## Technical Details

### Database Location
- File: `teachback.db` (in project root)
- Format: SQLite 3
- Automatic creation on first run

### Performance
- All database operations are wrapped in transactions
- Singleton pattern for database manager
- Graceful fallback if database fails

### Privacy
- All data stored locally
- No external sync (unless you implement it)
- Can be deleted by removing `teachback.db`

### Backup
To backup your data:
```bash
# Simple file copy
cp teachback.db teachback_backup.db

# Or export to SQL
sqlite3 teachback.db .dump > backup.sql
```

---

## Troubleshooting

### "No sessions found"
- Complete at least one teaching session in the main **"🎓 Teach"** tab
- Click the refresh button

### "Knowledge graph is empty"
- Teach at least one topic
- Wait for AI to extract related concepts (happens during session)

### "No reviews due"
- Great! You're caught up
- Complete more sessions to add topics to review queue

### Database errors
- Check that `teachback.db` isn't locked by another process
- Try restarting the app
- If corrupted, delete `teachback.db` (you'll lose history)

### Performance issues
- Large graphs (>50 nodes) may be slow
- Reduce the time range in progress tracker
- Database auto-optimizes, but you can vacuum manually:
  ```bash
  sqlite3 teachback.db "VACUUM;"
  ```

---

## Future Enhancements (Roadmap)

- [ ] Export sessions to PDF/Markdown
- [ ] Compare progress across different topics
- [ ] Social features (share knowledge graphs)
- [ ] Mobile app with sync
- [ ] Custom review schedules
- [ ] Gamification (achievements, levels)
- [ ] Multi-language support
- [ ] Voice-based reviews

---

## API Reference

For developers who want to extend the system:

### DatabaseManager
```python
from src.database.db_manager import DatabaseManager

db = DatabaseManager("teachback.db")

# Create user
db.get_or_create_user("user123", "John")

# Get sessions
sessions = db.get_user_sessions("user123", limit=10)

# Get stats
stats = db.get_user_stats("user123")
```

### KnowledgeGraphService
```python
from src.services.knowledge_graph import KnowledgeGraphService

kg = KnowledgeGraphService()

# Extract concepts
concepts = kg.extract_related_concepts(topic, conversation_history)

# Generate HTML
html = kg.generate_graph_html(graph_data)
```

### SpacedRepetitionService
```python
from src.services.spaced_repetition import SpacedRepetitionService

sr = SpacedRepetitionService(db_manager)

# Add topic
sr.add_topic_for_review("user123", "Quantum Physics")

# Get due reviews
due = sr.get_due_reviews("user123")

# Record review
sr.record_review(item_id=1, quality=4)
```

---

## Support

If you encounter issues or have questions:
1. Check this guide
2. Review the main README.md
3. Check GitHub Issues
4. Create a new issue with details

Happy learning! 🎓
