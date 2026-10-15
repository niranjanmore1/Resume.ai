import sqlite3, json, os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'resume.db')

def conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    c = conn()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS resumes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT, raw_text TEXT, skills TEXT,
            sections TEXT, contact TEXT, word_count INTEGER DEFAULT 0,
            domain TEXT DEFAULT 'general',
            created_at TEXT DEFAULT(datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS job_descriptions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jd_text TEXT, domain TEXT DEFAULT 'general',
            created_at TEXT DEFAULT(datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS results(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_id INTEGER, jd_id INTEGER,
            fit_score REAL DEFAULT 0, consistency_score REAL DEFAULT 0,
            tfidf_score REAL DEFAULT 0,
            component_scores TEXT, skill_analysis TEXT,
            keyword_analysis TEXT, section_strength TEXT,
            recommendations TEXT, roadmap TEXT,
            domain TEXT DEFAULT 'general',
            created_at TEXT DEFAULT(datetime('now'))
        );
    """)
    c.commit(); c.close()

def _all(q, p=()):
    c = conn(); rows = c.execute(q,p).fetchall(); c.close()
    return [dict(r) for r in rows]

def _one(q, p=()):
    c = conn(); row = c.execute(q,p).fetchone(); c.close()
    return dict(row) if row else None

def _run(q, p=()):
    c = conn(); cur = c.execute(q,p); lid = cur.lastrowid; c.commit(); c.close()
    return lid

def save_resume(parsed, filename, domain):
    return _run("INSERT INTO resumes(filename,raw_text,skills,sections,contact,word_count,domain)VALUES(?,?,?,?,?,?,?)",
        (filename, parsed.get('raw_text',''), json.dumps(parsed.get('skills',[])),
         json.dumps(parsed.get('sections',{})), json.dumps(parsed.get('contact',{})),
         parsed.get('word_count',0), domain))

def get_resume(rid):
    r = _one("SELECT * FROM resumes WHERE id=?", (rid,))
    if not r: return None
    r['skills']   = json.loads(r.get('skills') or '[]')
    r['sections'] = json.loads(r.get('sections') or '{}')
    r['contact']  = json.loads(r.get('contact') or '{}')
    return r

def save_jd(jd_text, domain):
    return _run("INSERT INTO job_descriptions(jd_text,domain)VALUES(?,?)", (jd_text, domain))

def save_result(rid, jid, scores, recs, roadmap):
    c = scores.get('consistency',{})
    return _run("""INSERT INTO results(resume_id,jd_id,fit_score,consistency_score,tfidf_score,
        component_scores,skill_analysis,keyword_analysis,section_strength,recommendations,roadmap,domain)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
        (rid, jid, scores.get('fit_score',0), c.get('consistency_score',0),
         scores.get('tfidf_similarity',0),
         json.dumps(scores.get('component_scores',{})), json.dumps(scores.get('skill_analysis',{})),
         json.dumps(scores.get('keyword_analysis',{})), json.dumps(scores.get('section_strength',{})),
         json.dumps(recs), json.dumps(roadmap), scores.get('domain','general')))

def get_result(rid):
    r = _one("SELECT * FROM results WHERE id=?", (rid,))
    if not r: return None
    for f in ['component_scores','skill_analysis','keyword_analysis','section_strength']:
        r[f] = json.loads(r.get(f) or '{}')
    for f in ['recommendations','roadmap']:
        r[f] = json.loads(r.get(f) or '[]')
    return r

def get_history(limit=50):
    return _all("""SELECT r.id as result_id, r.fit_score, r.consistency_score, r.domain,
        r.created_at, rs.filename, jd.jd_text
        FROM results r
        LEFT JOIN resumes rs ON r.resume_id=rs.id
        LEFT JOIN job_descriptions jd ON r.jd_id=jd.id
        ORDER BY r.created_at DESC LIMIT ?""", (limit,))

def get_dashboard_data():
    trend = _all("SELECT fit_score, consistency_score, created_at, domain FROM results ORDER BY created_at DESC LIMIT 10")
    domains = _all("SELECT domain, COUNT(*) as count FROM results GROUP BY domain")
    avg = _one("SELECT AVG(fit_score) as avg_fit, AVG(consistency_score) as avg_con, COUNT(*) as total FROM results")
    return {
        'score_trend': list(reversed(trend)),
        'domain_distribution': domains,
        'averages': avg or {},
        'total': avg.get('total',0) if avg else 0
    }