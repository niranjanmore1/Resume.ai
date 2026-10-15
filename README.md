# AutoResume AI 🎯

AI-powered resume builder, analyzer, and optimizer.

---

## 📁 Project Structure

```
autoresume-ai/
├── backend/
│   ├── app.py              ← Flask app + all API routes
│   ├── parser.py           ← PDF/DOCX text extraction + section parsing
│   ├── scorer.py           ← Fit score, TF-IDF, skill gap, consistency
│   ├── recommender.py      ← Actionable recommendations + roadmap
│   ├── database.py         ← SQLite ORM (resumes, JDs, results, history)
│   ├── skills_db.py        ← Domain skill lists + scoring weights
│   └── requirements.txt
├── frontend/
│   ├── index.html          ← Landing page
│   ├── builder.html        ← Resume builder form
│   ├── upload.html         ← Upload + JD input (2-step flow)
│   ├── results.html        ← Analysis results page
│   ├── dashboard.html      ← Charts + history
│   ├── style.css           ← Full design system
│   └── main.js             ← Shared utilities
├── data/
│   ├── uploads/            ← Uploaded resume files (auto-created)
│   └── resume_data.db      ← SQLite database (auto-created)
└── run.py                  ← Entry point
```

---

## 🚀 Step-by-Step Setup

### Step 1: Clone / create the project folder

```bash
mkdir autoresume-ai && cd autoresume-ai
```

### Step 2: Create a virtual environment

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### Step 3: Install backend dependencies

```bash
pip install -r backend/requirements.txt
```

### Step 4: Download NLTK data (one-time)

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### Step 5: Run the app

```bash
python run.py
```

Open your browser at: **http://localhost:5000**

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload_resume` | Upload PDF/DOCX resume |
| POST | `/api/build_resume` | Build resume from form data |
| POST | `/api/analyze_jd` | Analyze resume against JD |
| GET  | `/api/get_results/<id>` | Fetch full analysis result |
| GET  | `/api/history` | Get past analyses |
| GET  | `/api/dashboard_data` | Aggregated chart data |

---

## 🌐 Deployment (Render)

1. Push to GitHub
2. Create a new **Web Service** on [render.com](https://render.com)
3. Build command: `pip install -r backend/requirements.txt`
4. Start command: `python run.py`
5. Set environment: Python 3.11+

---

## 🧪 Testing the API

```bash
# Test upload
curl -X POST http://localhost:5000/api/upload_resume \
  -F "file=@myresume.pdf" \
  -F "domain=tech"

# Test JD analysis
curl -X POST http://localhost:5000/api/analyze_jd \
  -H "Content-Type: application/json" \
  -d '{"resume_id": 1, "jd_text": "We need a Python developer with 3 years experience in Flask and REST APIs...", "domain": "tech"}'

# Get results
curl http://localhost:5000/api/get_results/1
```

---

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, Flask 3.0 |
| NLP | NLTK, scikit-learn (TF-IDF) |
| PDF parsing | pdfplumber |
| DOCX parsing | python-docx |
| Database | SQLite (via stdlib sqlite3) |
| Frontend | HTML5, CSS3, Vanilla JS |
| Charts | Chart.js 4 |
| Fonts | Sora + DM Sans (Google Fonts) |
