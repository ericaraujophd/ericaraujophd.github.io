"""
make_delta_cv.py
----------------
Builds a 4-page version of Eric's CV for the DELTA Signature Course Fellowship
application (limit: "4 pages, single spaced") from his full RenderCV source.

Input : full.yaml               (copy of ericaraujophd.github.io/rendercv/Eric_Araújo_CV.yaml)
Output: Eric_Araujo_CV_DELTA.yaml  (render with: rendercv render Eric_Araujo_CV_DELTA.yaml)

Nothing is invented. Entries are copied from the full CV and only SELECTED or
SHORTENED, with these exceptions, all facts Eric has stated himself:
  * Education gains the M.Div. in progress at Calvin Theological Seminary.
  * Teaching gains the Cor Inquietum reading group (non-credit pilot, spring 2027).
  * The "Welcome" summary is rewritten to fit the course: CS, ABM research,
    Revisiting AI Ethics, the AI & STEM track, the M.Div.

Selection rule: keep what speaks to teaching, AI ethics, and faith and
technology (what DELTA reviewers read for); keep research in short form;
cut older talks, student lists and project descriptions, pointing to the
full CV on ericaraujo.com instead.
"""
import copy, yaml

full = yaml.safe_load(open("full.yaml", encoding="utf-8"))
cv = copy.deepcopy(full["cv"])
S = full["cv"]["sections"]          # the original sections, read-only
new = {}                            # the sections of the short CV, in order

# ---- Summary: two sentences in Eric's plain first-person voice.
new["Summary"] = [
    # Rewritten Nov 15, 2026 (approved by Eric): commitment to AI and ethics first,
    # the book last, no website link (it is already in the header).
    "I am a computer scientist at Calvin University who studies how opinions, emotions and "
    "behaviors spread through communities, using agent-based models. I am committed to "
    "helping Christians think well about artificial intelligence and the people it forms, "
    "in the classroom, at conferences and in the church. I led the AI & STEM track of "
    "Calvin's Wisdom in the Age of AI conference, will be part of Calvin's new Center for "
    "Faith and Technology, and am completing a Master of Divinity at Calvin Theological "
    "Seminary. I co-edit *Revisiting AI Ethics* (Springer, 2027).",
]

# ---- Education: add the M.Div. in progress (stated by Eric) at the top.
edu = copy.deepcopy(S["education"])
# Eric (Nov 15, 2026): he started the M.Div. in fall 2025; it is still in progress.
edu.insert(0, {"institution": "Calvin Theological Seminary", "area": "Divinity",
               "degree": "M.Div.", "start_date": "2025-09", "end_date": "present",
               "location": "Grand Rapids, MI"})
new["education"] = edu

# ---- Experience: all positions, highlights shortened to one line or removed.
exp = copy.deepcopy(S["experience"])
for e in exp:
    e.pop("highlights", None)
exp[1]["highlights"] = ["Research on the circulation of researchers in Brazilian health sciences."]
exp[2]["highlights"] = ["Criminology models with Prof. Dr. Charlotte Gerritsen."]
exp[3]["highlights"] = ["Thirteen years of teaching and graduate supervision in computer science."]
exp[4]["highlights"] = ["Professor and Coordinator of the Information Systems course."]
new["experience"] = exp

# ---- Teaching: current courses (one-line summaries) plus the Cor Inquietum pilot.
teach = copy.deepcopy(S["teaching"])
for t in teach:
    t.pop("summary", None)
# Name and summary updated Nov 14, 2026 (Eric) to match the final proposal.
teach.append({"code": "Cor Inquietum", "name": "*Cor Inquietum*: The Restless Heart in a Digital Age (reading group)",
              "location": "Calvin University USA", "date": "Spring 2027",
              "summary": "Non-credit pilot on the cardinal virtues, spiritual disciplines and digital technology; "
                         "basis of the proposed DELTA Signature Course, beginning in Calvin's Honors program."})
new["teaching"] = teach

# ---- Books (edited volume): unchanged.
new["books"] = copy.deepcopy(S["books"])

# ---- Selected publications: recent journal work, the thesis, and the
#      polarization / social-contagion papers closest to the course.
keep_pubs = [1, 3, 4, 9, 13, 15, 18, 26]
new["selected_publications"] = [copy.deepcopy(S["publications"][i]) for i in keep_pubs]

# ---- Selected talks: faith, technology and AI venues.
keep_talk_names = ["Wisdom in the Age of AI Conference", "Baylor Symposium", "American Academy of Religion",
                   "American Scientific Affiliation"]
talks = [copy.deepcopy(t) for t in S["events"] if any(k in t["name"] for k in keep_talk_names)]
for t in talks:   # one-line summaries keep the section short
    if "Baylor" in t["name"]:
        t["summary"] = '"Cognitive Modeling of Christian Communities: Developing Intelligent Agents to Address the Polarization Effects in Churches."'
    if "Prompted" in t["name"]:
        t["summary"] = "Podcast guest on what large language models know about women of the early church."
    if "Wisdom in the Age of AI" in t["name"]:
        t["summary"] = '"Modeling Communities in Peril: Polarization and the Changes in the Social Fabric of Congregations through an Agent-Based Approach."'
    if "American Academy of Religion" in t["name"]:
        t["summary"] = "Empirical evaluation of LLM accuracy on Macrina the Younger and Olympias of Constantinople."
talks.sort(key=lambda t: t["year"], reverse=True)
new["selected_talks"] = talks

# ---- Grants and fellowships: all, summaries shortened.
gf = copy.deepcopy(S["grants_and_fellowships"])
short = {
 "Templeton": "$100,000 planning grant (Listening and Learning in a Polarized World), co-led with Dr. Damaris Parsitau, on agent-based models of congregations in Brazil and Kenya.",
 "Hoogeboom": "Inaugural award, supporting a summer research placement for student David Quinn on the church-polarization project.",
 "Calvin Research Fellowship": "Four load hours in 2026-2027 for \"Modeling Political and Religious Polarization in Christian Communities.\" Diekema Fellow.",
}
for g in gf:
    for k, v in short.items():
        if k in g["name"]:
            g["summary"] = v
new["grants_and_fellowships"] = gf

# ---- Research projects: the two faith-and-technology projects plus Procores, one line each.
proj = [copy.deepcopy(p) for p in S["research_projects"] if p["name"].startswith(("Matristics", "CS Prayers", "Procores"))]
for p in proj:
    p["highlights"] = p["highlights"][:1]
    if p["name"].startswith("Procores"):
        p["highlights"] = ["Research group on social networks, contagion processes and complex data (CNPq Universal 2022)."]
new["research_projects"] = proj

# ---- Student supervision: Calvin projects closest to the course, then a count for Brazil.
calvin_keep = ["Sally Amonoo-Mensah", "Ian Hawthorne", "Miriam Crisman", "Adam Byle", "Katelin Jandris", "Jaden Brookens"]
seen, sup = set(), []
for s in S["supervised_students"]:
    if any(s["name"].startswith(k) for k in calvin_keep) and s["name"] not in seen:
        e = copy.deepcopy(s); e.pop("highlights", None); sup.append(e); seen.add(s["name"])
sup.append({"name": "Graduate and undergraduate students", "location": "UFLA and UFSC — Brazil",
            "date": "2011 - 2025",
            "summary": "Supervised one Ph.D. dissertation, seven M.S. theses and nineteen undergraduate theses and research projects."})
new["supervised_students"] = sup

# ---- Service, church and professional development: the faith-and-learning items.
us = copy.deepcopy(S["university_service"])
for u in us:   # summaries shortened to one line
    if u["name"].startswith("Track Leader"):
        u["summary"] = "Led the AI & STEM track (October 8-10, 2026, more than 600 participants)."
    elif u["name"].startswith("Faculty Advisor, Girls Who Code"):
        u["summary"] = "Includes leading the student delegation to the Grace Hopper Celebration."
    else:
        u.pop("summary", None)
new["university_service"] = us
new["professional_service"] = copy.deepcopy(S["professional_service"][:1])
new["church_and_community_service"] = copy.deepcopy(S["church_and_community_service"])
pd = [copy.deepcopy(p) for p in S["professional_development"] if not p["name"].startswith("Healthy Dialogue")]
for p in pd:   # one line each
    if p["name"].startswith("G&M"):
        p["location"] = "Grace & Mercy Foundation, New York"
        p["summary"] = "On the public reading of Scripture and the Just Show Up book club at Calvin."
    if p["name"].startswith("Faith & Learning"):
        p["location"] = "de Vries Institute, Calvin University"
        p["summary"] = "On integrating Christian faith with scholarly work."
    if p["name"].startswith("Kuiper"):
        p["summary"] = "Year-long seminar on faith and learning, pedagogy and the Reformed tradition."
new["professional_development"] = pd

cv["sections"] = new
# ---- Layout: same classic theme as the full CV, 10 pt body text (single spaced),
#      tighter margins and spacing, entries allowed to break across pages so
#      no half-empty pages are left, and no "x years y months" lines.
# ---- Order (Eric, Nov 15, 2026): Books and Selected Publications come last.
for key in ("books", "selected_publications"):
    new[key] = new.pop(key)

design = {
    "theme": "classic",
    "page": {"size": "us-letter", "top_margin": "0.6in", "bottom_margin": "0.6in",
             "left_margin": "0.65in", "right_margin": "0.65in", "show_top_note": False},
    "header": {"photo_width": "2.6cm", "space_below_name": "0.4cm", "space_below_headline": "0.4cm",
               "space_below_connections": "0.4cm"},
    "section_titles": {"space_above": "0.35cm", "space_below": "0.2cm"},
    "sections": {"allow_page_break": True, "space_between_regular_entries": "0.8em",
                 "show_time_spans_in": []},
    # Nov 14: entries kept whole, so the Cor Inquietum pilot is not split across pages.
    "entries": {"allow_page_break": False},
    # Nov 15, 2026 (Eric, option A): calmer slate blue and soft charcoal body text,
    # the same colors as his main CV.
    "colors": {"body": "rgb(46, 52, 64)", "name": "rgb(62, 92, 118)", "headline": "rgb(62, 92, 118)",
               "connections": "rgb(62, 92, 118)", "section_titles": "rgb(62, 92, 118)",
               "links": "rgb(62, 92, 118)"},
}
out = {"cv": cv, "design": design}
yaml.safe_dump(out, open("Eric_Araujo_CV_DELTA.yaml", "w", encoding="utf-8"), allow_unicode=True, sort_keys=False, width=100)
print("written")
