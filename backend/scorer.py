import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from skills_db import SKILLS_DB
from parser import extract_skills

def tfidf_sim(a, b):
    if not a or not b or len(a.split()) < 3 or len(b.split()) < 3:
        return 0.0
    try:
        v = TfidfVectorizer(stop_words='english', ngram_range=(1,2), min_df=1)
        m = v.fit_transform([a, b])
        raw = float(cosine_similarity(m[0:1], m[1:2])[0][0])
        # Scale: raw cosine for related docs is 0.05-0.25, scale to 0-100
        return round(min(raw * 5.0, 1.0), 4)
    except:
        return 0.0

def keyword_overlap(resume_text, jd_text):
    def words(t):
        return set(w.lower() for w in re.findall(r'\b[a-zA-Z][a-zA-Z0-9+#.]{2,}\b', t)
                   if w.lower() not in {'the','and','for','with','that','this','are','was','have','from','will','been','they','their','your','you','our','can','not','but','all','has'})
    rw = words(resume_text)
    jw = words(jd_text)
    matched = rw & jw
    missing = jw - rw
    pct = len(matched) / max(len(jw), 1)
    return {
        'matched_keywords': sorted(list(matched))[:30],
        'missing_keywords': sorted(list(missing))[:30],
        'keyword_match_pct': round(pct, 4)
    }

def skill_gap(resume_skills, jd_text, domain):
    jd_skills = extract_skills(jd_text, domain)
    rs = {s.lower() for s in resume_skills}
    js = {s.lower() for s in jd_skills}
    matched = rs & js
    missing = js - rs
    extra   = rs - js
    pct = len(matched) / max(len(js), 1) if js else 0.5
    return {
        'jd_skills':      sorted(list(js)),
        'matched_skills': sorted(list(matched)),
        'missing_skills': sorted(list(missing)),
        'extra_skills':   sorted(list(extra)),
        'skill_match_pct': round(min(pct, 1.0), 4)
    }

def bias_score(resume, jd_text, domain, skill_pct, tfidf):
    w = SKILLS_DB.get(domain, SKILLS_DB['general'])['weights']
    sec = resume.get('sections', {})
    raw = resume.get('raw_text', '')

    proj = sec.get('projects','') or ''
    exp  = sec.get('experience','') or ''
    edu  = sec.get('education','') or ''

    # If sections are empty fall back to full text
    if len((proj+exp).split()) < 20:
        proj = raw; exp = raw

    ps = tfidf_sim(proj, jd_text) if proj else 0.25
    es = tfidf_sim(exp,  jd_text) if exp  else 0.25
    ed = 0.6 if edu else 0.3  # education neutral

    comp = {'skills': skill_pct, 'projects': ps, 'experience': es, 'education': ed}
    total = sum(comp[k] * w[k] for k in w)

    # 55% weighted + 45% TF-IDF
    blended = (total * 0.55) + (tfidf * 0.45)

    # Floor: if resume has content give at least 15
    if raw and len(raw.split()) > 50:
        blended = max(blended, 0.15)

    fit = round(min(blended * 100, 100), 1)
    return {
        'fit_score': fit,
        'component_scores': {k: round(v*100,1) for k,v in comp.items()},
        'tfidf_similarity': round(tfidf*100, 1)
    }

def consistency(resume, domain):
    skills = resume.get('skills', [])
    sec = resume.get('sections', {})
    ctx = (sec.get('projects','') + ' ' + sec.get('experience','') + ' ' + resume.get('raw_text','')).lower()
    ok, bad = [], []
    for s in skills:
        if re.search(r'\b' + re.escape(s.lower()) + r'\b', ctx):
            ok.append(s)
        else:
            bad.append(s)
    total = len(skills)
    score = (len(ok)/total*100) if total else 50.0
    return {'consistency_score': round(score,1), 'validated_skills': ok, 'unvalidated_skills': bad, 'total_skills': total}

def section_strength(resume):
    sec = resume.get('sections', {})
    thresh = {'summary':30,'skills':10,'experience':80,'projects':60,'education':20,'achievements':15}
    return {k: round(min(len(sec.get(k,'').split())/t*100, 100), 1) for k,t in thresh.items()}

def compute_full_score(resume, jd_text, domain):
    raw    = resume.get('raw_text','')
    skills = resume.get('skills',[])
    sim    = tfidf_sim(raw, jd_text)
    kw     = keyword_overlap(raw, jd_text)
    sg     = skill_gap(skills, jd_text, domain)
    bs     = bias_score(resume, jd_text, domain, sg['skill_match_pct'], sim)
    con    = consistency(resume, domain)
    ss     = section_strength(resume)
    return {
        'fit_score':        bs['fit_score'],
        'component_scores': bs['component_scores'],
        'tfidf_similarity': bs['tfidf_similarity'],
        'skill_analysis':   sg,
        'keyword_analysis': kw,
        'consistency':      con,
        'section_strength': ss,
        'domain':           domain
    }