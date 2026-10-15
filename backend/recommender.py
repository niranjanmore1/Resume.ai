from skills_db import get_yt

def generate_recommendations(scores, domain):
    recs = []
    sa   = scores.get('skill_analysis',{})
    con  = scores.get('consistency',{})
    ss   = scores.get('section_strength',{})
    fit  = scores.get('fit_score',0)
    miss = sa.get('missing_skills',[])

    if miss:
        recs.append({"priority":"high","icon":"🎯","category":"Skill Gap",
            "title":f"Add {len(miss)} missing skills to your resume",
            "detail":f"JD requires: {', '.join(miss[:4])}{'...' if len(miss)>4 else ''}. Include these explicitly — ATS scans for exact matches."})

    bad = con.get('unvalidated_skills',[])
    if bad:
        recs.append({"priority":"high","icon":"⚠️","category":"Consistency",
            "title":f"{len(bad)} skills listed but not demonstrated in projects/experience",
            "detail":f"'{', '.join(bad[:3])}' appear in skills but not in projects or work experience. Add concrete examples for each."})

    if fit < 40:
        recs.append({"priority":"high","icon":"🔄","category":"Overall Fit",
            "title":"Resume needs significant tailoring",
            "detail":"Score below 40%. Rewrite your summary using exact JD language. Mirror the job title and key requirements."})
    elif fit < 65:
        recs.append({"priority":"medium","icon":"📈","category":"Overall Fit",
            "title":"Tailor resume more specifically to this role",
            "detail":"Use exact phrases from the JD in your summary and bullet points. Quantify achievements (%, $, counts)."})

    kw = scores.get('keyword_analysis',{}).get('keyword_match_pct',0)
    if kw < 0.25:
        recs.append({"priority":"medium","icon":"🤖","category":"ATS Optimization",
            "title":"Low keyword overlap with job description",
            "detail":"ATS filters reject resumes with <30% keyword match. Use exact terms from the posting, not synonyms."})

    for sec, pct in ss.items():
        if pct < 40:
            recs.append({"priority":"medium" if pct>10 else "high","icon":"📝","category":"Section",
                "title":f"Strengthen {sec.title()} section ({pct:.0f}% complete)",
                "detail":_tip(sec)})

    recs.append({"priority":"low","icon":"📊","category":"Impact",
        "title":"Quantify every achievement with numbers",
        "detail":"'Reduced load time by 40%', 'Led 5 engineers', 'Grew revenue by ₹2L/mo' — numbers make bullets memorable."})

    order = {"high":0,"medium":1,"low":2}
    recs.sort(key=lambda x: order.get(x['priority'],3))
    return recs

def generate_roadmap(missing_skills, domain):
    roadmap = []
    for i, skill in enumerate(missing_skills[:6]):
        yt = get_yt(skill)
        roadmap.append({
            "step": i+1,
            "skill": skill,
            "timeline": f"Week {i*2+1}–{i*2+2}",
            "action": f"Learn {skill} fundamentals, then build a small hands-on project",
            "yt_title": yt['title'],
            "yt_url":   yt['url'],
            "yt_ch":    yt['ch'],
            "priority": "high" if i < 2 else "medium"
        })
    return roadmap

def _tip(sec):
    tips = {
        "summary":     "Write 3–4 sentences: strengths, years of experience, and value you bring. Tailor it per application.",
        "skills":      "List 12–20 skills using exact terms from job postings. Group by: Languages, Frameworks, Tools, Databases.",
        "experience":  "3–5 bullets per role using STAR format. Start each with an action verb. Quantify every outcome.",
        "projects":    "3–5 projects with: name, tech stack, your role, measurable outcome, and GitHub link.",
        "education":   "Degree, institution, year, relevant coursework. Add GPA only if above 3.5.",
        "achievements":"Certifications, awards, publications — include the issuing body and date."
    }
    return tips.get(sec, "Add more specific, relevant details to this section.")