# 🚀 Automated-Spoken-Rubric-Scorer

AI-powered Transcript Scoring Tool for Spoken Communication Assessment

**Automated-Spoken-Rubric-Scorer** is an end-to-end evaluation system that analyzes a student's spoken communication or written transcripts using **rule-based logic**, **semantic NLP models**, and a **rubric-driven scoring engine**.

## 📌 Features

- Rule-based scoring  
- NLP semantic similarity scoring  
- Rubric-driven evaluation  
- Web UI + JSON API  
- Detailed scoring breakdown  

## 🏗️ Project Architecture
```
speechscore-ai/
├── frontend/
├── backend/
├── testing/
└── README.md
```

## ⚙️ Tech Stack

**Backend:** Python, FastAPI, Sentence-Transformers  
**Frontend:** HTML, CSS, JavaScript  

# 🚀 Getting Started

### 1️⃣ Clone the repository
```
git clone https://github.com/<your-username>/speechscore-ai
cd speechscore-ai
```

### 2️⃣ Install backend dependencies
```
pip install -r backend/requirements.txt
```

### 3️⃣ Run the backend
```
uvicorn backend.app:app --reload
```

API will run at:  
➡️ **http://localhost:8000/score**

### 4️⃣ Open the frontend
Open the file:
```
frontend/index.html
```
(or run using VS Code Live Server)

## 🧪 Testing

The **testing/** folder includes:

- **20 Perfect Score Samples**  
- **Realistic student transcripts**  
- **Edge-case transcripts** (short, long, missing keywords)

These help validate the scoring engine thoroughly.

---

Sujal Pokale
