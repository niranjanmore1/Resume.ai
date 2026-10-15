import re, os
from skills_db import SKILLS_DB

def _clean(text):
    text = re.sub(r'\s+', ' ', text)
    return re.sub(r'[^\x00-\x7F]+',' ', text).strip()

def extract_text(path):
    ext = path.rsplit('.',1)[-1].lower()
    if ext == 'pdf':
        try:
            import pdfplumber
            with pdfplumber.open(path) as pdf:
                return '\n'.join(p.extract_text() or '' for p in pdf.pages)
        except Exception as e:
            raise ValueError(f'PDF parse error: {e}')
    elif ext in ('docx','doc'):
        try:
            from docx import Document
            return '\n'.join(p.text for p in Document(path).paragraphs if p.text.strip())
        except Exception as e:
            raise ValueError(f'DOCX parse error: {e}')
    raise ValueError(f'Unsupported format: {ext}')

SECTION_KEYS = {
    'education':   ['education','academic','degree','university','college','qualification'],
    'skills':      ['skills','technical','technologies','tools','competencies','expertise'],
    'experience':  ['experience','employment','work history','professional','career','internship'],
    'projects':    ['projects','portfolio','personal projects','academic projects'],
    'achievements':['achievements','awards','certifications','honors','accomplishments'],
    'summary':     ['summary','objective','profile','about','overview']
}

def parse_sections(text):
    lines = text.split('\n')
    sections = {k:[] for k in SECTION_KEYS}
    sections['other'] = []
    cur = 'other'
    for line in lines:
        line = line.strip()
        if not line: continue
        ll = line.lower()
        matched = False
        if len(ll) < 60:
            for sec, kws in SECTION_KEYS.items():
                if any(kw in ll for kw in kws):
                    cur = sec; matched = True; break
        if not matched:
            sections[cur].append(line)
    return {k: '\n'.join(v) for k,v in sections.items()}

def extract_skills(text, domain='general'):
    text_lower = text.lower()
    found = []
    for skill in SKILLS_DB.get(domain, SKILLS_DB['general'])['skills']:
        if re.search(r'\b' + re.escape(skill.lower()) + r'\b', text_lower):
            found.append(skill)
    # Also check all domains for cross-domain skills
    for d, data in SKILLS_DB.items():
        if d == domain: continue
        for skill in data['skills'][:20]:  # top 20 from other domains
            if skill not in found and re.search(r'\b' + re.escape(skill.lower()) + r'\b', text_lower):
                found.append(skill)
    return list(set(found))

def extract_contact(text):
    c = {}
    m = re.search(r'[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}', text)
    if m: c['email'] = m.group()
    m = re.search(r'(\+?\d[\d\s\-().]{7,14}\d)', text)
    if m: c['phone'] = m.group().strip()
    m = re.search(r'linkedin\.com/in/([\w-]+)', text, re.I)
    if m: c['linkedin'] = 'linkedin.com/in/' + m.group(1)
    m = re.search(r'github\.com/([\w-]+)', text, re.I)
    if m: c['github'] = 'github.com/' + m.group(1)
    return c

def _process(raw, domain):
    clean = _clean(raw)
    sections = parse_sections(clean)
    skills   = extract_skills(clean, domain)
    contact  = extract_contact(clean)
    return {
        'raw_text':   clean,
        'sections':   sections,
        'skills':     skills,
        'contact':    contact,
        'word_count': len(clean.split())
    }

def parse_resume_file(path, domain='general'):
    raw = extract_text(path)
    if not raw or len(raw.strip()) < 20:
        raise ValueError('Could not extract text from file. Make sure it is not a scanned image.')
    return _process(raw, domain)

def parse_resume_text(raw, domain='general'):
    return _process(raw, domain)