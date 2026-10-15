import os, sys, uuid, json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, '..', 'frontend')
DATA_DIR     = os.path.join(BASE_DIR, '..', 'data')
UPLOAD_DIR   = os.path.join(DATA_DIR, 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

sys.path.insert(0, BASE_DIR)
from database      import init_db, save_resume, get_resume, save_jd, save_result, get_result, get_history, get_dashboard_data
from parser  import parse_resume_file, parse_resume_text
from scorer  import compute_full_score
from recommender    import generate_recommendations, generate_roadmap

init_db()

ALLOWED = {'pdf','docx','doc'}
def allowed(fn): return '.' in fn and fn.rsplit('.',1)[1].lower() in ALLOWED
def ok(d):   return jsonify({"success": True,  **d})
def err(m,c=400): return jsonify({"success": False, "error": m}), c

@app.route('/')
def index(): return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:p>')
def static_files(p):
    try:    return send_from_directory(FRONTEND_DIR, p)
    except: return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/api/upload_resume', methods=['POST'])
def upload_resume():
    if 'file' not in request.files: return err('No file provided')
    f = request.files['file']
    domain = request.form.get('domain','general')
    if not f.filename: return err('No file selected')
    if not allowed(f.filename): return err('Only PDF and DOCX supported')
    ext  = f.filename.rsplit('.',1)[1].lower()
    name = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(UPLOAD_DIR, name)
    f.save(path)
    try:
        parsed = parse_resume_file(path, domain)
    except Exception as e:
        os.remove(path)
        return err(str(e))
    rid = save_resume(parsed, f.filename, domain)
    return ok({'resume_id': rid, 'skills': parsed['skills'],
               'contact': parsed['contact'], 'word_count': parsed['word_count'],
               'sections_found': [k for k,v in parsed['sections'].items() if v.strip()]})

@app.route('/api/analyze_jd', methods=['POST'])
def analyze_jd():
    body = request.get_json()
    if not body: return err('JSON body required')
    rid    = body.get('resume_id')
    jd     = body.get('jd_text','').strip()
    domain = body.get('domain','general')
    if not rid: return err('resume_id required')
    if not jd or len(jd) < 30: return err('Job description too short')
    resume = get_resume(rid)
    if not resume: return err('Resume not found', 404)
    scores = compute_full_score(resume, jd, domain)
    missing = scores.get('skill_analysis',{}).get('missing_skills',[])
    recs    = generate_recommendations(scores, domain)
    roadmap = generate_roadmap(missing, domain)
    jid     = save_jd(jd, domain)
    result_id = save_result(rid, jid, scores, recs, roadmap)
    return ok({'result_id': result_id, 'fit_score': scores['fit_score'],
               'consistency_score': scores['consistency']['consistency_score']})

@app.route('/api/get_results/<int:rid>', methods=['GET'])
def get_results(rid):
    r = get_result(rid)
    if not r: return err('Result not found', 404)
    return ok({'result': r})

@app.route('/api/history', methods=['GET'])
def history():
    limit = request.args.get('limit', 50, type=int)
    return ok({'history': get_history(limit)})

@app.route('/api/dashboard_data', methods=['GET'])
def dashboard():
    return ok({'dashboard': get_dashboard_data()})

@app.route('/api/job_roles', methods=['GET'])
def job_roles():
    from skills_db import JOB_ROLES, DOMAIN_LABELS
    domain = request.args.get('domain','tech')
    return ok({'roles': JOB_ROLES.get(domain, []), 'domain_label': DOMAIN_LABELS.get(domain,'')})

@app.route('/api/build_resume', methods=['POST'])
def build_resume():
    body = request.get_json()
    if not body: return err('JSON body required')
    domain = body.get('domain','general')
    p = body.get('personal',{})
    raw = f"""
{p.get('name','')}
{p.get('email','')} | {p.get('phone','')} | {p.get('linkedin','')}

SUMMARY
{p.get('summary','')}

EDUCATION
{chr(10).join([f"{e.get('degree','')} in {e.get('field','')} — {e.get('institution','')} ({e.get('year','')})" for e in body.get('education',[])])}

SKILLS
{', '.join(body.get('skills',[]))}

EXPERIENCE
{chr(10).join([f"{e.get('title','')} at {e.get('company','')} ({e.get('duration','')}) {e.get('description','')}" for e in body.get('experience',[])])}

PROJECTS
{chr(10).join([f"{pr.get('name','')}: {pr.get('description','')} | Tech: {pr.get('tech','')}" for pr in body.get('projects',[])])}

ACHIEVEMENTS
{chr(10).join(body.get('achievements',[]))}
""".strip()
    parsed = parse_resume_text(raw, domain)
    rid = save_resume(parsed, 'built_resume.txt', domain)
    return ok({'resume_id': rid, 'skills': parsed['skills']})

if __name__ == '__main__':
    print("\n🎯 AutoResume AI running at http://localhost:5000\n")
    app.run(debug=True, port=5000, host='0.0.0.0')