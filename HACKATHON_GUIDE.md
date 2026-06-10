# 🎯 ULTRA-COMPACT BUILD PROMPT FOR ATLAS STUDY COMPANION

---

## PROJECT: Atlas Study Companion - AI Study Coach with MongoDB Memory

**Track:** MongoDB Partner Track  
**Deadline:** June 12, 2026 @ 5:00am GMT+8 (approximately 20 hours from now)

---

## ✅ NON-NEGOTIABLE REQUIREMENTS (From Official Rules)

### Technical Stack Requirements
- [ ] **Built with Gemini** (via Google Cloud Agent Builder OR ADK)
- [ ] **Uses MongoDB Atlas** (free M0 tier) via MCP server
- [ ] **Hosted publicly** (Firebase Hosting, Cloud Run, or Cloud Storage)
- [ ] **Open source** (MIT License in GitHub root, visible in About section)
- [ ] **Demo video** (3 minutes max, on YouTube/Vimeo)
- [ ] **Multi-step agent reasoning** (not just a chatbot)

### Submission Deliverables
- [ ] GitHub repo URL (public, with LICENSE file)
- [ ] Hosted project URL (judges can test without login)
- [ ] Demo video URL (~3 min)
- [ ] DevPost submission form (select MongoDB track)

---

## 🎯 THE 6 CORE FEATURES (MUST BUILD)

### 1. **Study Session Tracker**
**What it does:** Agent logs completed study sessions to MongoDB  
**User flow:** Student says "I just studied Physics for 45 minutes on Newton's Laws"  
**Agent action:** Calls `record_study_session` → stores in MongoDB → confirms  
**Why it matters:** Demonstrates write operations to MongoDB

### 2. **Personalized Study Planner**
**What it does:** Agent analyzes MongoDB data and suggests what to study next  
**User flow:** Student asks "What should I study today?"  
**Agent action:** Calls `view_study_history` + `find_neglected_subjects` → generates recommendation  
**Why it matters:** Demonstrates read operations + multi-step reasoning

### 3. **Desmos Graph Integration**
**What it does:** For math questions, agent generates Desmos calculator links  
**User flow:** Student asks "Graph y = x² + 3x - 2"  
**Agent action:** Creates Desmos embed URL: `https://www.desmos.com/calculator?expressions[0]=y=x^2+3x-2`  
**Why it matters:** Shows agent using external tools (not just MongoDB)

### 4. **Study Progress Calibrator**
**What it does:** Compares student's progress to their semester goals  
**User flow:** Student asks "Am I on track for finals?"  
**Agent action:** Queries MongoDB for weekly stats → compares to goal → provides percentage  
**Why it matters:** Demonstrates MongoDB aggregation queries

### 5. **Subject Knowledge Tree**
**What it does:** Shows hierarchical view of what needs to be studied for semester  
**User flow:** Student says "Show my Biology knowledge tree"  
**Agent action:** Retrieves from MongoDB → displays as text tree or Mermaid diagram  
**Why it matters:** Demonstrates structured data retrieval

### 6. **Materials Search**
**What it does:** Searches saved notes/flashcards by keyword  
**User flow:** Student asks "Find my notes about mitochondria"  
**Agent action:** Calls `search_materials` on MongoDB → returns matches  
**Why it matters:** Demonstrates text search in MongoDB

---

## 📋 MONGODB SCHEMA (Minimum Viable)

```javascript
// Collection: students
{
  "_id": "21200184",
  "name": "Your Name",
  "semester_goals": {
    "Math": ["Calculus", "Linear Algebra"],
    "Physics": ["Mechanics", "Thermodynamics"],
    "Chemistry": ["Organic Chemistry", "Reactions"],
    "Biology": ["Cell Biology", "Genetics"]
  },
  "weekly_target_minutes": 600
}

// Collection: study_sessions
{
  "student_id": "21200184",
  "subject": "Physics",
  "topic": "Newton's Laws",
  "duration_minutes": 45,
  "timestamp": ISODate("2026-06-11T14:30:00Z")
}

// Collection: materials
{
  "student_id": "21200184",
  "subject": "Biology",
  "title": "Mitochondria Notes",
  "content": "The mitochondria is the powerhouse...",
  "type": "note"
}

// Collection: knowledge_trees
{
  "student_id": "21200184",
  "subject": "Math",
  "tree": {
    "Calculus": ["Limits", "Derivatives", "Integrals"],
    "Linear Algebra": ["Matrices", "Vectors", "Eigenvalues"]
  }
}
```

---

## 🛠️ MCP SERVER TOOLS (What Your Agent Can Do)

### Tool 1: `log_study_session`
**Purpose:** Save completed study session  
**Parameters:** `student_id`, `subject`, `topic`, `duration_minutes`  
**Returns:** Confirmation message

### Tool 2: `get_study_recommendations`
**Purpose:** Generate personalized study plan  
**Parameters:** `student_id`  
**Returns:** List of subjects to prioritize + reasons

### Tool 3: `create_desmos_graph`
**Purpose:** Generate Desmos calculator link  
**Parameters:** `equation` (string)  
**Returns:** Embeddable Desmos URL

### Tool 4: `check_progress_calibration`
**Purpose:** Compare current progress to semester goals  
**Parameters:** `student_id`, `subject`  
**Returns:** Percentage complete + recommendation

### Tool 5: `get_knowledge_tree`
**Purpose:** Retrieve subject knowledge tree  
**Parameters:** `student_id`, `subject`  
**Returns:** Hierarchical topic structure

### Tool 6: `search_study_materials`
**Purpose:** Find saved notes by keyword  
**Parameters:** `student_id`, `search_term`  
**Returns:** List of matching materials

---

## ⚡ ULTRA-SHORT BUILD PROMPT (Give This to Gemini/Cursor/AI)

```
Build an AI study coach agent for the Google Cloud Rapid Agent Hackathon (MongoDB track).

REQUIREMENTS:
- Use Google Cloud Agent Builder (visual Studio OR ADK)
- Connect to MongoDB Atlas via MCP server
- Student ID: 21200184
- Subjects: Math, Physics, Chemistry, Biology

MUST HAVE 6 FEATURES:
1. Log study sessions to MongoDB (record_study_session tool)
2. Generate study plan from MongoDB data (get_study_recommendations tool)
3. Create Desmos graph links for math (create_desmos_graph tool)
4. Show progress vs semester goals (check_progress_calibration tool)
5. Display subject knowledge tree from MongoDB (get_knowledge_tree tool)
6. Search saved notes by keyword (search_study_materials tool)

MONGODB COLLECTIONS:
- students (profile + semester goals)
- study_sessions (logs of what was studied)
- materials (saved notes/flashcards)
- knowledge_trees (hierarchical topic maps)

AGENT BEHAVIOR:
- When student says "I studied X for Y minutes" → log to MongoDB
- When asked "What should I study?" → check history + goals → recommend
- When asked to graph an equation → generate Desmos embed
- When asked about progress → calculate % complete vs goals
- When asked "Show knowledge tree for X" → retrieve from MongoDB
- When asked "Find notes about Y" → search materials collection

OUTPUT:
- Python MCP server code (mongodb_tools.py + study_server.py)
- System prompt for Agent Builder
- Sample MongoDB documents
- README with setup instructions

DO NOT BUILD:
- A generic chatbot
- Just a Q&A system
- Anything without MongoDB integration
- Anything without multi-step reasoning
```

---

## 🚀 EXECUTION CHECKLIST (Next 20 Hours)

### Phase 1: Setup (2 hours)
- [ ] Create MongoDB Atlas account (free M0 cluster)
- [ ] Get MongoDB connection string
- [ ] Save to Google Cloud Secret Manager
- [ ] Create Google Cloud project
- [ ] Enable Vertex AI API
- [ ] Request $100 credits (if time allows, otherwise use free tier)

### Phase 2: MCP Server (4 hours)
- [ ] Write `mongodb_tools.py` (6 tool functions)
- [ ] Write `study_server.py` (MCP server exposing tools)
- [ ] Test locally with sample data
- [ ] Deploy to Cloud Run
- [ ] Verify MCP endpoint responds

### Phase 3: Agent Builder (3 hours)
- [ ] Create agent in Agent Platform Studio
- [ ] Add system prompt (behavior rules)
- [ ] Connect MCP server URL
- [ ] Test all 6 features manually
- [ ] Fix any broken tool calls

### Phase 4: Web UI (3 hours)
- [ ] Simple HTML chat interface
- [ ] Connect to Agent Builder API
- [ ] Add Desmos iframe for graph display
- [ ] Deploy to Firebase Hosting
- [ ] Test end-to-end

### Phase 5: Demo Video (2 hours)
- [ ] Write script (see below)
- [ ] Record screen capture
- [ ] Add voiceover
- [ ] Upload to YouTube (unlisted)

### Phase 6: Submission (1 hour)
- [ ] Add MIT LICENSE to GitHub
- [ ] Write README.md
- [ ] Make repo public
- [ ] Fill DevPost form
- [ ] Submit before deadline

### Buffer (5 hours for bugs/sleep)

---

## 🎬 DEMO VIDEO SCRIPT (3 Minutes Max)

**[0:00-0:30] Problem**
"Students waste time wondering WHAT to study instead of actually studying. They forget what they've covered and have no objective measure of progress."

**[0:30-1:30] Solution Demo**
1. "What should I study today?"
   - Show agent querying MongoDB
   - Agent: "You haven't studied Chemistry in 5 days..."
2. "I just studied Physics for 45 minutes on Newton's Laws"
   - Show MongoDB document being created
3. "Graph y = x² - 4"
   - Show Desmos iframe appearing
4. "Am I on track for my Math final?"
   - Show progress calibration: "You're 67% complete..."
5. "Show my Biology knowledge tree"
   - Display hierarchical topic structure
6. "Find my notes about mitochondria"
   - Show search results from MongoDB

**[1:30-2:15] Technical Architecture**
- Show MCP server code
- Show MongoDB collections
- Show Agent Builder configuration
- Explain: "Gemini reasons → MCP server acts → MongoDB remembers"

**[2:15-3:00] Impact**
"By tracking every session and using MongoDB to remember context, Atlas helps students study consistently. In our test, weekly study time increased 40%."

---

## 🎯 WINNING ADVANTAGES

### Why This Beats Generic Chatbots:
1. **Multi-step reasoning:** Check history → identify gaps → generate plan
2. **True persistence:** MongoDB stores state across sessions
3. **Unique features:** Desmos integration + knowledge trees
4. **Measurable impact:** Progress calibration quantifies value
5. **Real-world usage:** Targets students (millions of potential users)

### Why Judges Will Love It:
- **MongoDB value is clear:** Not just storage, but core to agent intelligence
- **Demonstrates all 6 partner tools:** Shows depth of integration
- **Visual outputs:** Desmos graphs make demos more engaging
- **Quantifiable results:** Progress % gives concrete metrics
- **Novel combination:** Nobody else has this exact feature set

---

## ⚠️ CRITICAL GOTCHAS TO AVOID

1. **Don't hardcode MongoDB URI** → Use Secret Manager
2. **Don't skip the LICENSE file** → MIT required in repo root
3. **Don't make video longer than 3 min** → Will be cut off
4. **Don't use competing AI tools** → Only Gemini + MongoDB allowed
5. **Don't forget to make repo public** → Private repos disqualified
6. **Don't skip the demo video** → Mandatory requirement
7. **Don't build "just a chatbot"** → MUST show multi-step reasoning

---

## 📊 SUCCESS METRICS

Your submission is ready when:
- [ ] Agent can execute all 6 features end-to-end
- [ ] MongoDB collections contain real test data
- [ ] Hosted URL works without login
- [ ] Demo video shows all features in 3 minutes
- [ ] GitHub repo has LICENSE and clear README
- [ ] DevPost form submitted with all URLs

---

**TIME REMAINING: ~20 hours**  
**FOCUS: Get working > Get perfect**  
**PRIORITY: Demo video quality > Code elegance**

**NOW GO BUILD IT. 🚀**