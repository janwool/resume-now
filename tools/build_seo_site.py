#!/usr/bin/env python3
"""Generate crawlable SEO landing pages from the resume template catalog."""

from __future__ import annotations

import html
import json
import re
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
SITE = "https://resume-now.online"
TODAY = date.today().isoformat()


def load_templates():
    source = (ROOT / "template-manifest.js").read_text(encoding="utf-8")
    payload = re.sub(r"^\s*window\.resumeTemplateManifest\s*=\s*", "", source)
    payload = re.sub(r";\s*$", "", payload)
    return json.loads(payload)


TEMPLATES = load_templates()


CATEGORIES = {
    "ats": ("ATS-Friendly Resume Templates", "Clean, readable resume templates built around straightforward headings and scannable content."),
    "professional": ("Professional Resume Templates", "Polished resume templates for business, operations, finance, consulting, and experienced candidates."),
    "minimal": ("Minimal Resume Templates", "Quiet typography, generous whitespace, and a clear hierarchy that keeps attention on your experience."),
    "modern": ("Modern Resume Templates", "Contemporary layouts with confident typography and a fresh, structured presentation."),
    "creative": ("Creative Resume Templates", "Expressive layouts for design, media, marketing, photography, and other portfolio-led careers."),
    "simple": ("Simple Resume Templates", "Uncomplicated resume layouts that are easy to scan, edit, and tailor for each application."),
    "executive": ("Executive Resume Templates", "Confident resume designs for directors, senior leaders, founders, and experienced professionals."),
    "student": ("Student Resume Templates", "Flexible resume templates for students, internships, recent graduates, and first professional roles."),
    "one-page": ("One-Page Resume Templates", "Compact layouts designed to present your most relevant qualifications on one focused page."),
    "two-column": ("Two-Column Resume Templates", "Structured two-column layouts that balance skills, contact details, and work history."),
}


GUIDES = {
    "how-to-write-a-resume": {
        "title": "How to Write a Resume in 2026: A Practical Step-by-Step Guide",
        "description": "Learn how to write a focused resume, choose the right format, build each section, and tailor it for a job application.",
        "intro": "A strong resume is a short, evidence-led case for why you fit a particular role. It is not a complete autobiography. The best version makes the next decision easy for a recruiter: invite this person to an interview.",
        "sections": [
            ("1. Start with the job, not the template", "Read the job description and note the repeated skills, outcomes, tools, and level of responsibility. Choose a template only after you know what information needs the most space. A simple single-column layout suits dense technical experience; a balanced two-column layout can work well when skills and certifications matter."),
            ("2. Choose the right resume format", "Use reverse chronological order when your recent work history is your strongest evidence. Choose a functional structure sparingly, usually when you need to foreground transferable skills. A combination resume blends a strong skills summary with a concise chronological history."),
            ("3. Write a specific headline and summary", "Name the role you are targeting and summarize your relevant scope in two to four lines. Replace broad claims such as ‘hard-working professional’ with concrete context: years of experience, domain, type of customers, scale, or a representative outcome."),
            ("4. Turn responsibilities into achievements", "Begin bullets with a clear action, explain what changed, and quantify the result when the number is meaningful. ‘Managed weekly reporting’ is weaker than ‘Automated weekly revenue reporting, cutting preparation time from five hours to forty minutes.’"),
            ("5. Make skills easy to verify", "List skills that appear in the job description only when your experience supports them. Group related tools and avoid progress bars: an applicant tracking system and a human reader both benefit from plain skill names."),
            ("6. Edit for clarity", "Remove filler, unexplained acronyms, first-person pronouns, and repeated phrases. Check dates, tense, capitalization, contact details, and line breaks. Export to PDF only after reviewing the final page at normal zoom."),
            ("7. Tailor and proofread every application", "Keep one complete master resume, then make a focused copy for each role. Reorder bullets to surface relevant evidence, mirror the employer’s terminology naturally, and ask another person to check the final document."),
        ],
        "faq": [("How long should a resume be?", "One page is a useful target for early-career candidates. Two pages are appropriate when relevant experience genuinely needs the space."), ("Should every resume be ATS-friendly?", "Every resume should use clear headings and readable text. Highly visual layouts are better reserved for situations where a person will review the file directly."), ("What file type should I send?", "Follow the employer’s instructions. PDF usually preserves layout best; use DOCX when the application explicitly requests it.")],
    },
    "cv-vs-resume": {
        "title": "CV vs Resume: The Difference and Which One to Use",
        "description": "Understand the difference between a CV and resume, including regional usage, length, content, and when employers expect each document.",
        "intro": "The meaning of CV and resume changes by country and industry. In the United States, a resume is usually a concise job application document, while an academic CV is a comprehensive record. In many other markets, CV is simply the common name for the document Americans call a resume.",
        "sections": [("Resume", "A resume is tailored to a specific role and usually runs one or two pages. It prioritizes relevant work, skills, education, and measurable achievements."), ("Academic CV", "An academic CV is much longer and can include research, publications, teaching, grants, conferences, awards, and professional service. It grows throughout a career."), ("Regional terminology", "Employers in the UK, Europe, parts of Asia, and other regions commonly ask for a CV when they expect a concise employment document. Always follow the language in the job posting."), ("How to decide", "Use a tailored resume for most private-sector applications in North America. Use a full academic CV for research, faculty, medical, or grant contexts. Elsewhere, use the employer’s preferred term and match local conventions.")],
        "faq": [("Can I use the same template?", "Yes for most job-search CVs. Academic CVs need a more document-like layout that can grow across many pages."), ("Is a CV always longer?", "Not internationally. A standard UK CV is commonly two pages, while a US academic CV can be much longer.")],
    },
    "resume-summary": {
        "title": "How to Write a Resume Summary, With Examples",
        "description": "Write a concise resume summary that communicates your target role, relevant experience, strengths, and evidence in a few lines.",
        "intro": "A resume summary should help a recruiter understand your fit before reading the work history. The useful version is specific, evidence-based, and tailored; the weak version is a stack of adjectives.",
        "sections": [("Use a four-part formula", "Combine your professional identity, relevant experience, strongest specialty, and one useful proof point. Example: ‘B2B product marketer with six years of SaaS experience, specializing in go-to-market strategy and lifecycle campaigns that improved qualified pipeline by 28%.’"), ("Match the role’s language", "Use the normal title and terminology for the target role. Do not stuff keywords or copy the posting word for word; make each phrase defensible in your experience section."), ("Examples by career stage", "Student: lead with degree, relevant projects, internship, and target. Career changer: connect transferable expertise to the new function. Experienced candidate: name scope, domain, leadership, and a representative result."), ("What to remove", "Delete ‘seeking a challenging position,’ vague enthusiasm, personal pronouns, unsupported superlatives, and objectives centered only on what you want.")],
        "faq": [("How long should a summary be?", "Two to four concise lines are usually enough."), ("Do students need a summary?", "Use one when it adds relevant context; otherwise projects, education, and skills can begin the page."), ("Summary or objective?", "A summary emphasizes evidence. An objective can help when your target needs explanation, such as a career change.")],
    },
    "make-resume-stand-out": {
        "title": "How to Make Your Resume Stand Out Without Gimmicks",
        "description": "Make your resume more memorable through relevance, evidence, hierarchy, and clear writing—not visual tricks or unsupported claims.",
        "intro": "Standing out does not mean being louder. It means making relevant evidence easier to find and believe than it is on the average application.",
        "sections": [("Lead with relevance", "Put the experience most closely related to the job near the top and give it more space. A recruiter should understand your fit in the first screen or upper third of the page."), ("Show outcomes", "Use numbers when they clarify scale, speed, quality, revenue, cost, adoption, reliability, or customer impact. Explain what you changed, not merely what your team was responsible for."), ("Build visual hierarchy", "Use consistent headings, spacing, dates, and bullet styles. One accent color can guide the eye; too many decorative elements compete with the content."), ("Include proof", "Add portfolio, GitHub, publication, or project links when they are relevant and current. Label links clearly so the reader knows what they will see."), ("Tailor the first half", "You rarely need to rewrite everything. A targeted headline, summary, skills order, and first two recent roles usually create the greatest difference.")],
        "faq": [("Should I use color?", "A restrained accent is fine for many roles, but readability and contrast come first."), ("Do unusual fonts help?", "Usually not. Familiar, highly readable fonts make the document feel more intentional."), ("Should I add a photo?", "Follow regional norms. Photos are uncommon in US applications and may be discouraged.")],
    },
    "resume-skills": {
        "title": "Skills for a Resume: How to Choose and Present Them",
        "description": "Choose relevant hard and soft skills, place them effectively, and support them with evidence throughout your resume.",
        "intro": "A skills section works best as an index to evidence elsewhere in the resume. It should help a reader scan; it should not ask them to accept a long list without proof.",
        "sections": [("Prioritize hard skills", "Start with tools, methods, languages, certifications, or domain knowledge required for the role. Use the exact common name rather than creative synonyms."), ("Prove soft skills in context", "Communication, leadership, and problem solving become credible when a bullet shows who you worked with, what you decided, and what improved."), ("Group long lists", "Organize related skills under short labels such as Data, Design, Platforms, or Languages. Keep the labels plain enough for both recruiters and parsers."), ("Use proficiency carefully", "Avoid arbitrary five-star ratings. For spoken languages, standard levels can help; for tools, experience and project context are usually stronger evidence."), ("Remove weak signals", "Do not list basic office skills unless the role requests them. Remove outdated tools, interests presented as skills, and keywords you could not discuss in an interview.")],
        "faq": [("How many skills should I list?", "List the most relevant set you can support—often eight to fifteen, depending on the role."), ("Where should skills go?", "Near the top for technical roles or career changes; after experience when your work history is the stronger proof."), ("Can I copy skills from the job ad?", "Use matching terms only when they accurately describe your ability.")],
    },
    "ats-friendly-resume": {
        "title": "How to Make an ATS-Friendly Resume",
        "description": "Create an ATS-friendly resume with clear structure, standard headings, useful keywords, and a readable PDF or DOCX file.",
        "intro": "Applicant tracking systems store and organize applications; the exact screening process varies by employer. You cannot guarantee a score, but you can make your resume easier to parse and easier for a recruiter to review.",
        "sections": [("Use recognizable headings", "Experience, Education, Skills, Certifications, and Projects are clear. Clever labels can hide information from both software and hurried readers."), ("Keep important text as text", "Do not place core qualifications only inside images, charts, icons, or decorative graphics. Contact details and job titles should be selectable text."), ("Use keywords naturally", "Match relevant terminology from the job posting in context. Repetition without evidence does not make a stronger application and can reduce readability."), ("Choose a conservative layout when needed", "Single-column designs are the lowest-risk option. Simple two-column resumes can work, but test the exported file by selecting and copying its text in reading order."), ("Follow the upload instructions", "Use PDF when allowed and the text remains selectable. Use DOCX when requested. Name the file professionally with your name and role.")],
        "faq": [("Can any template guarantee ATS approval?", "No. Hiring systems and employer workflows differ, and qualification still depends on the role."), ("Are columns always bad?", "No, but complex reading order raises risk. Use a simpler layout for high-volume application portals."), ("Should I hide keywords?", "No. Hidden or white text is deceptive and can make the document unusable.")],
    },
    "resume-format-in-word": {
        "title": "How to Format a Resume in Microsoft Word",
        "description": "Set margins, typography, headings, spacing, and page breaks for a clean resume in Microsoft Word, then export it correctly.",
        "intro": "Word can produce a professional resume when the document uses a small set of consistent styles. The goal is not to position every line manually; it is to build a layout that stays stable when content changes.",
        "sections": [("Set the page first", "Choose Letter or A4 based on the market, then use margins around 0.6 to 0.85 inches. Avoid shrinking margins and text merely to force one page."), ("Create a type system", "Use one readable family, a clear name size, consistent section headings, and 10–12 point body text. Set paragraph spacing rather than adding empty lines."), ("Use tables carefully", "Borderless tables can align dates and headings, but deeply nested tables can complicate editing. Avoid text boxes for essential content because reading order may become unpredictable."), ("Control page breaks", "Keep a heading with the paragraph that follows it and prevent a job heading from becoming an orphan at the bottom of a page. Review every page after edits."), ("Export and test", "Save the editable source, export a PDF, open it independently, copy the text to confirm reading order, and check links. ResumeNowOnline currently provides online editing and PDF downloads; it does not claim a Word export.")],
        "faq": [("Should I submit DOCX or PDF?", "Use the employer’s requested format. PDF preserves layout; DOCX may be required by some systems."), ("Which font works best?", "Readable fonts such as Aptos, Arial, Calibri, Georgia, or Times New Roman are safe choices."), ("Can I use a Word template here?", "ResumeNowOnline templates are edited in the browser and exported as PDF.")],
    },
    "resume-bullet-points": {
        "title": "Resume Bullet Points: Write Stronger Achievement Statements",
        "description": "Turn job responsibilities into concise resume bullet points that explain your action, context, and measurable outcome.",
        "intro": "A good bullet is a compact unit of evidence. It tells the reader what you did, where the difficulty or scale was, and why the work mattered.",
        "sections": [("Use action + context + result", "Start with the decision or action, add the important scope, then state the outcome. Not every bullet needs a number, but every bullet should convey a useful change or contribution."), ("Choose precise verbs", "Use verbs such as analyzed, designed, launched, negotiated, automated, reduced, or mentored. Avoid repeating ‘managed’ when a more exact action exists."), ("Quantify honestly", "Use ranges or operational measures when revenue numbers are confidential: cycle time, volume, team size, adoption, defect rate, retention, or customer satisfaction."), ("Keep one idea per bullet", "Dense multi-sentence bullets are hard to scan. Split unrelated outcomes and prioritize the most relevant three to six bullets for each recent role."), ("Examples", "Weak: ‘Responsible for customer onboarding.’ Stronger: ‘Redesigned onboarding for 1,200 monthly users, reducing first-week support tickets by 19%.’")],
        "faq": [("How long should a bullet be?", "Aim for one or two lines in the final layout."), ("How many bullets per job?", "Three to six for recent relevant roles; fewer for older positions."), ("Do all bullets need numbers?", "No. Specific scope and clear outcomes can be meaningful without a metric.")],
    },
    "how-long-should-a-resume-be": {
        "title": "How Long Should a Resume Be? One Page vs Two Pages",
        "description": "Decide whether your resume should be one or two pages based on career stage, relevance, industry, and the strength of your evidence.",
        "intro": "The right length is the shortest version that communicates enough relevant evidence. One page is not a universal rule, and two pages are not automatically more senior.",
        "sections": [("Choose one page when", "You are a student, recent graduate, early-career candidate, or making a focused change with limited directly relevant history. A tight page also works for experienced candidates whose strongest evidence is recent."), ("Choose two pages when", "You have substantial relevant experience, leadership scope, technical projects, certifications, publications, or achievements that would become cramped or illegible on one page."), ("Cut before shrinking", "Remove outdated and unrelated details, repetitive bullets, objective statements, references, and basic skills. Keep readable body text and usable margins."), ("Make page two worthwhile", "Continue with meaningful experience; do not let a few orphaned lines create a second page. Repeat your name and page number only if it helps the reader."), ("Academic and specialist exceptions", "Academic CVs, federal resumes, medical credentials, and some international formats follow different expectations. Use the required convention.")],
        "faq": [("Is a three-page resume ever acceptable?", "It can be for specialized or executive contexts, but most private-sector applications benefit from tighter editing."), ("Will ATS reject two pages?", "No general rule makes two pages invalid."), ("Should I remove older jobs?", "Summarize or omit older work when it no longer supports the target role.")],
    },
    "cover-letter-for-resume": {
        "title": "How to Write a Cover Letter That Complements Your Resume",
        "description": "Write a focused cover letter that adds motivation, context, and fit without repeating every bullet from your resume.",
        "intro": "Your resume supplies structured evidence. Your cover letter connects that evidence to this employer and explains the parts of your candidacy that a list of jobs cannot.",
        "sections": [("Open with a reason", "Name the role and offer a specific reason for your interest: the product, mission, customer problem, team, or kind of work. Avoid generic enthusiasm that could be sent anywhere."), ("Choose two proof points", "Select the most relevant achievements from your resume and add context: the challenge, your judgment, the collaboration, and the outcome."), ("Address useful context", "A cover letter can explain a deliberate career change, relocation, portfolio direction, or unusual experience. Keep the explanation forward-looking."), ("Close with fit", "Summarize what you can contribute and invite a conversation. You do not need formal or overly deferential language."), ("Keep the documents consistent", "Use the same name, contact details, typography, and tone across both documents. Proofread company and hiring manager names carefully.")],
        "faq": [("How long should a cover letter be?", "Usually 250–400 words on one page."), ("Should I always send one?", "Send one when requested and when it can add real context; a tailored letter can help even when optional."), ("Can I reuse a cover letter?", "Reuse the structure, but tailor the opening, proof points, and employer connection.")],
    },
}


JOBS = {
    "software-engineer": ("Software Engineer Resume Example", ["Software development", "System design", "Testing", "Cloud platforms", "Cross-functional delivery"], ["Reduced API latency by 38% by redesigning caching and database access patterns.", "Led migration of twelve services to automated deployment with zero planned downtime.", "Raised critical-path test coverage from 61% to 89% and cut regression incidents."]),
    "product-manager": ("Product Manager Resume Example", ["Product strategy", "Roadmapping", "User research", "Analytics", "Stakeholder alignment"], ["Defined onboarding roadmap that increased activation by 17% over two quarters.", "Synthesized forty customer interviews into a prioritized enterprise feature plan.", "Aligned design, engineering, and sales around measurable quarterly outcomes."]),
    "project-manager": ("Project Manager Resume Example", ["Project planning", "Risk management", "Budgeting", "Vendor coordination", "Executive reporting"], ["Delivered a multi-region platform rollout three weeks ahead of schedule.", "Introduced risk reviews that reduced late milestone changes by 31%.", "Managed a $1.8M program across four vendors and six internal teams."]),
    "data-analyst": ("Data Analyst Resume Example", ["SQL", "Data visualization", "Experiment analysis", "Forecasting", "Data quality"], ["Built a retention dashboard used in weekly decisions by five product teams.", "Identified checkout friction that informed a change worth 9% more conversions.", "Automated recurring reporting and saved analysts twenty hours each month."]),
    "accountant": ("Accountant Resume Example", ["Financial reporting", "Reconciliation", "Month-end close", "Tax compliance", "ERP systems"], ["Shortened month-end close from eight business days to five.", "Reconciled 140 accounts and resolved a six-figure historical discrepancy.", "Standardized expense controls across three business units."]),
    "financial-analyst": ("Financial Analyst Resume Example", ["Financial modeling", "Forecasting", "Variance analysis", "Scenario planning", "Executive presentations"], ["Built a scenario model that guided a $4M capacity investment.", "Improved quarterly forecast accuracy by 12 percentage points.", "Translated operating variances into actions for regional leaders."]),
    "marketing-manager": ("Marketing Manager Resume Example", ["Campaign strategy", "Demand generation", "Content", "Marketing analytics", "Team leadership"], ["Launched an integrated campaign that generated $2.1M in qualified pipeline.", "Reduced paid acquisition cost by 24% through creative and audience testing.", "Built a quarterly content program with sales and subject-matter experts."]),
    "sales-representative": ("Sales Representative Resume Example", ["Prospecting", "Discovery", "Negotiation", "CRM", "Account growth"], ["Finished at 124% of annual quota across a mid-market territory.", "Created a discovery framework that raised qualified opportunity rate by 16%.", "Expanded twelve existing accounts through needs-led proposals."]),
    "administrative-assistant": ("Administrative Assistant Resume Example", ["Calendar management", "Travel coordination", "Documentation", "Office operations", "Confidentiality"], ["Coordinated complex calendars for four leaders across three time zones.", "Introduced a travel workflow that reduced booking changes by 27%.", "Organized board materials and maintained accurate confidential records."]),
    "customer-service": ("Customer Service Resume Example", ["Customer support", "Case management", "De-escalation", "Product knowledge", "Quality assurance"], ["Maintained a 96% satisfaction score across more than 1,500 cases.", "Created help-center content that reduced repeat questions by 14%.", "Coached six new representatives on de-escalation and case documentation."]),
    "graphic-designer": ("Graphic Designer Resume Example", ["Visual design", "Brand systems", "Typography", "Adobe Creative Suite", "Creative collaboration"], ["Created a modular campaign system used across nine markets.", "Cut production time by 30% by building reusable design components.", "Partnered with marketing to refresh a product launch across web and print."]),
    "teacher": ("Teacher Resume Example", ["Curriculum planning", "Classroom management", "Assessment", "Family communication", "Differentiated instruction"], ["Improved grade-level reading proficiency by 18 percentage points.", "Designed differentiated lessons for a class of thirty-two learners.", "Led a teaching team that aligned assessment and intervention plans."]),
    "nurse": ("Registered Nurse Resume Example", ["Patient care", "Clinical assessment", "Care coordination", "Patient education", "Electronic health records"], ["Coordinated safe care for up to six acute patients per shift.", "Improved discharge education compliance through a standardized checklist.", "Precepted eight new nurses on unit procedures and documentation."]),
    "executive-assistant": ("Executive Assistant Resume Example", ["Executive support", "Complex scheduling", "Board coordination", "Events", "Operational judgment"], ["Managed priorities and scheduling for a CEO and two senior executives.", "Coordinated quarterly board meetings, materials, and follow-up actions.", "Planned a 180-person leadership event within budget and timeline."]),
    "student-internship": ("Student Internship Resume Example", ["Coursework", "Projects", "Research", "Communication", "Learning agility"], ["Analyzed survey data for a capstone project and presented recommendations.", "Coordinated a student event attended by 240 participants.", "Built a working prototype with a four-person interdisciplinary team."]),
}


def esc(value):
    return html.escape(str(value), quote=True)


def write_route(route, content):
    folder = DIST if route == "/" else DIST / route.strip("/")
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "index.html").write_text(content, encoding="utf-8")


def schema_json(data):
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def header():
    return """<header class=\"seo-nav\"><a class=\"brand\" href=\"/\"><img class=\"brand-icon\" src=\"/assets/brand/resume-now-mark-v2-64.png\" alt=\"\" width=\"25\" height=\"25\">ResumeNowOnline</a><nav aria-label=\"Main navigation\"><a href=\"/resume-templates/\">Templates</a><a href=\"/resume-examples/\">Examples</a><a href=\"/career-advice/\">Career advice</a><a href=\"/pricing.html\">Pricing</a></nav><a class=\"button button--primary button--small\" href=\"/builder.html\">Build my resume</a></header>"""


def footer():
    return """<footer class=\"seo-footer\"><div><a class=\"brand\" href=\"/\"><img class=\"brand-icon\" src=\"/assets/brand/resume-now-mark-v2-64.png\" alt=\"\" width=\"25\" height=\"25\">ResumeNowOnline</a><p>Edit any resume online for free. Pay $5 only when you need three PDF downloads.</p></div><div><strong>Build</strong><a href=\"/resume-templates/\">Resume templates</a><a href=\"/cv-templates/\">CV templates</a><a href=\"/resume-examples/\">Resume examples</a><a href=\"/pricing.html\">Pricing</a></div><div><strong>Learn</strong><a href=\"/career-advice/how-to-write-a-resume/\">How to write a resume</a><a href=\"/career-advice/ats-friendly-resume/\">ATS-friendly resumes</a><a href=\"/resume-format/\">Resume formats</a><a href=\"/career-advice/cv-vs-resume/\">CV vs resume</a></div><div><strong>Company</strong><a href=\"/contact.html\">Contact</a><a href=\"/privacy.html\">Privacy</a><a href=\"/terms.html\">Terms</a><a href=\"/refunds.html\">Refunds</a></div></footer>"""


def page(title, description, path, body, schemas, image="/assets/template-previews/template-001.jpg", robots="index,follow"):
    canonical = SITE + path
    schema_blocks = "".join(f'<script type="application/ld+json">{schema_json(item)}</script>' for item in schemas)
    return f"""<!doctype html><html lang=\"en\"><head><meta charset=\"UTF-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>{esc(title)}</title><meta name=\"description\" content=\"{esc(description)}\"><meta name=\"robots\" content=\"{robots}\"><link rel=\"canonical\" href=\"{canonical}\"><meta property=\"og:type\" content=\"website\"><meta property=\"og:site_name\" content=\"ResumeNowOnline\"><meta property=\"og:title\" content=\"{esc(title)}\"><meta property=\"og:description\" content=\"{esc(description)}\"><meta property=\"og:url\" content=\"{canonical}\"><meta property=\"og:image\" content=\"{SITE}{image}\"><meta name=\"twitter:card\" content=\"summary_large_image\"><meta name=\"twitter:title\" content=\"{esc(title)}\"><meta name=\"twitter:description\" content=\"{esc(description)}\"><meta name=\"twitter:image\" content=\"{SITE}{image}\"><link rel=\"icon\" type=\"image/png\" sizes=\"32x32\" href=\"/assets/brand/favicon-v2-32.png\"><link rel=\"apple-touch-icon\" href=\"/assets/brand/apple-touch-icon-v2.png\"><link rel=\"stylesheet\" href=\"/styles.css?v=40\">{schema_blocks}</head><body class=\"seo-page\">{header()}<main>{body}</main>{footer()}</body></html>"""


def breadcrumb(items):
    links = []
    schema_items = []
    for index, (label, url) in enumerate(items, 1):
        links.append(f'<a href="{url}">{esc(label)}</a>')
        schema_items.append({"@type": "ListItem", "position": index, "name": label, "item": SITE + url})
    return '<nav class="seo-breadcrumb" aria-label="Breadcrumb">' + '<span aria-hidden="true">/</span>'.join(links) + '</nav>', {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": schema_items}


def template_tags(template):
    name = template["name"].lower()
    tags = {"professional"}
    rules = {
        "ats": ("ats", "classic", "clean", "simple", "essential", "monochrome", "recruiter", "traditional"),
        "minimal": ("minimal", "clean", "simple", "essential", "monochrome"),
        "modern": ("modern", "contemporary", "bold", "fresh", "timeline", "geometric", "sidebar"),
        "creative": ("creative", "designer", "photographer", "portfolio", "editorial", "visual", "color"),
        "executive": ("executive", "leadership", "director", "senior", "corporate", "consultant"),
        "student": ("student", "graduate", "entry", "intern"),
        "one-page": ("one-page", "compact", "concise"),
        "two-column": ("two-column", "sidebar", "split", "column"),
        "simple": ("simple", "classic", "clean", "essential", "traditional", "minimal"),
    }
    for tag, words in rules.items():
        if any(word in name for word in words):
            tags.add(tag)
    return tags


def card(template):
    return f'''<article class="seo-template-card"><a href="/resume-templates/{esc(template["slug"])}/"><img src="/{esc(template["preview"])}" alt="{esc(template["name"])} preview" loading="lazy" width="420" height="594"></a><div><p>{esc(template["subtitle"])}</p><h2><a href="/resume-templates/{esc(template["slug"])}/">{esc(template["name"])}</a></h2><a class="seo-text-link" href="/builder.html?template={esc(template["id"])}">Edit this template free →</a></div></article>'''


def faq_markup(items):
    visible = "".join(f'<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in items)
    schema = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in items]}
    return f'<section class="seo-faq"><div class="seo-section-heading"><span>Questions, answered</span><h2>Resume FAQ</h2></div>{visible}</section>', schema


def generate_template_pages():
    for template in TEMPLATES:
        title = f'{template["name"]} — Edit Online'
        desc = f'Customize the {template["name"]} online for free. Edit every section, preview your resume, and get three PDF downloads for $5.'
        path = f'/resume-templates/{template["slug"]}/'
        crumb, crumb_schema = breadcrumb([("Home", "/"), ("Resume templates", "/resume-templates/"), (template["name"], path)])
        pages = sorted((ROOT / "assets" / "template-pages" / template["id"]).glob("page-*.jpg"))
        previews = pages or [ROOT / template["preview"]]
        gallery = "".join(f'<figure><img src="/{esc(p.relative_to(ROOT).as_posix())}" alt="{esc(template["name"])} page {i}" loading="lazy"><figcaption>Page {i}</figcaption></figure>' for i, p in enumerate(previews, 1))
        tags = sorted(template_tags(template))
        category_links = "".join(f'<a href="/resume-templates/{tag}/">{esc(tag.replace("-", " ").title())}</a>' for tag in tags if tag in CATEGORIES)
        faq, faq_schema = faq_markup([("Is this resume template free to edit?", "Yes. You can open the template and edit its content in the browser without paying."), ("What does a download cost?", "One $5 purchase includes three PDF downloads. There is no subscription."), ("Can I edit the whole resume?", "Yes. Select text and supported elements directly on the resume canvas; available controls appear beside the document."), ("Does the editor preserve every template page?", "Yes. The editor loads the template’s available pages and keeps its visual layout while you make changes.")])
        product_schema = {"@context": "https://schema.org", "@type": "SoftwareApplication", "name": template["name"], "applicationCategory": "BusinessApplication", "operatingSystem": "Web", "description": desc, "url": SITE + path, "image": SITE + "/" + template["preview"], "offers": [{"@type": "Offer", "name": "Online editing", "price": "0", "priceCurrency": "USD"}, {"@type": "Offer", "name": "Three PDF downloads", "price": "5", "priceCurrency": "USD"}], "publisher": {"@type": "Organization", "name": "ResumeNowOnline", "url": SITE}}
        body = f'''<div class="seo-shell">{crumb}<section class="seo-template-hero"><div><span class="seo-kicker">Free to edit · $5 for 3 downloads</span><h1>{esc(template["name"])}</h1><p class="seo-lede">{esc(template["subtitle"])}. Keep the original visual design, replace the sample content directly on the resume, and download only when you are ready.</p><div class="seo-actions"><a class="button button--primary" href="/builder.html?template={esc(template["id"])}">Use this template</a><a class="button button--outline" href="#preview">Preview all pages</a></div><ul class="seo-checks"><li>Edit the complete resume online</li><li>All available template pages included</li><li>No subscription or recurring charge</li></ul></div><div class="seo-hero-preview"><img src="/{esc(template["preview"])}" alt="{esc(template["name"])} full preview"></div></section><section class="seo-copy-grid"><div><span class="seo-kicker">Designed for real applications</span><h2>A structured starting point, ready for your experience</h2><p>This {esc(', '.join(tags[:3]))} resume template gives your name, profile, experience, education, and skills a deliberate visual hierarchy. Replace the example text with evidence from your own work and tailor the first half of the document to the role.</p><p>For the cleanest result, keep bullets concise, use consistent dates, and remove any section that does not strengthen the application. Review every page before exporting.</p><div class="seo-tag-list">{category_links}</div></div><aside class="seo-note"><strong>Transparent pricing</strong><p>Editing and previewing are free. A single $5 payment adds three PDF download credits to your account.</p><a href="/pricing.html">See pricing details →</a></aside></section><section class="seo-preview-section" id="preview"><div class="seo-section-heading"><span>Template preview</span><h2>See every included page</h2><p>The editor opens the same template shown here—not just its colors.</p></div><div class="seo-page-gallery">{gallery}</div></section>{faq}<section class="seo-final-cta"><span>Ready to make it yours?</span><h2>Edit this resume online for free.</h2><p>Pay only when you want three PDF downloads.</p><a class="button button--light" href="/builder.html?template={esc(template["id"])}">Start editing</a></section></div>'''
        write_route(path, page(title, desc, path, body, [product_schema, crumb_schema, faq_schema], "/" + template["preview"]))


def generate_catalog():
    path = "/resume-templates/"
    crumb, crumb_schema = breadcrumb([("Home", "/"), ("Resume templates", path)])
    category_nav = "".join(f'<a href="/resume-templates/{slug}/">{esc(title.replace(" Resume Templates", ""))}</a>' for slug, (title, _) in CATEGORIES.items())
    body = f'''<div class="seo-shell">{crumb}<section class="seo-listing-hero"><span class="seo-kicker">105 editable designs</span><h1>Free Resume Templates You Can Edit Online</h1><p class="seo-lede">Choose a resume template, edit the complete document for free, and pay $5 only when you need three PDF downloads. No subscription.</p><div class="seo-actions"><a class="button button--primary" href="/builder.html">Build my resume</a><a class="button button--outline" href="#templates">Browse all templates</a></div></section><nav class="seo-chip-nav" aria-label="Template categories">{category_nav}</nav><section class="seo-editorial"><h2>Choose a resume template for the way you want to be read</h2><div><p>A strong layout makes your most relevant evidence easy to find. Start with a simple or ATS-friendly design for application portals, a professional layout for broad business roles, or a more expressive template when visual judgment is part of the work.</p><p>Every design below opens as the actual template in the editor. You can change text across all included pages and adjust supported elements without rebuilding the resume from scratch.</p></div></section><section id="templates"><div class="seo-section-heading"><span>Complete collection</span><h2>All resume templates</h2></div><div class="seo-template-grid">{"".join(card(t) for t in TEMPLATES)}</div></section><section class="seo-final-cta"><span>Simple pricing</span><h2>Edit free. Download when ready.</h2><p>One $5 payment includes three PDF downloads.</p><a class="button button--light" href="/builder.html">Start with a blank choice</a></section></div>'''
    collection = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Free Resume Templates", "description": "105 editable resume templates", "url": SITE + path, "mainEntity": {"@type": "ItemList", "numberOfItems": len(TEMPLATES), "itemListElement": [{"@type": "ListItem", "position": i, "url": f'{SITE}/resume-templates/{t["slug"]}/', "name": t["name"]} for i, t in enumerate(TEMPLATES, 1)]}}
    write_route(path, page("Free Resume Templates to Edit Online | ResumeNowOnline", "Browse 105 free editable resume templates. Customize the full resume online and get three PDF downloads for a one-time $5 payment.", path, body, [collection, crumb_schema]))


def generate_categories():
    for slug, (title, description) in CATEGORIES.items():
        selected = [t for t in TEMPLATES if slug in template_tags(t)]
        if not selected:
            continue
        path = f"/resume-templates/{slug}/"
        crumb, crumb_schema = breadcrumb([("Home", "/"), ("Resume templates", "/resume-templates/"), (title, path)])
        faq, faq_schema = faq_markup([("Can I edit these templates for free?", "Yes. Editing and previewing are free."), ("How much do downloads cost?", "Three PDF downloads cost $5 as a one-time purchase."), ("Which template should I choose?", "Choose the layout that gives your most relevant experience enough room and matches the expectations of your target role.")])
        body = f'''<div class="seo-shell">{crumb}<section class="seo-listing-hero"><span class="seo-kicker">Curated collection · {len(selected)} designs</span><h1>{esc(title)}</h1><p class="seo-lede">{esc(description)} Edit every section online for free, then pay $5 if you need three PDF downloads.</p><div class="seo-actions"><a class="button button--primary" href="#templates">Choose a template</a><a class="button button--outline" href="/resume-templates/">View all 105</a></div></section><section class="seo-editorial"><h2>When this resume style works best</h2><div><p>{esc(description)} The right choice still depends on your content: prioritize readable text, consistent headings, and enough space for concrete achievements.</p><p>Start with the original design, replace the sample content directly, and keep only the sections that help a recruiter assess your fit. For automated application portals, test the exported PDF’s selectable text and reading order.</p></div></section><section id="templates"><div class="seo-template-grid">{"".join(card(t) for t in selected)}</div></section>{faq}</div>'''
        collection = {"@context": "https://schema.org", "@type": "CollectionPage", "name": title, "description": description, "url": SITE + path, "mainEntity": {"@type": "ItemList", "numberOfItems": len(selected), "itemListElement": [{"@type": "ListItem", "position": i, "url": f'{SITE}/resume-templates/{t["slug"]}/', "name": t["name"]} for i, t in enumerate(selected, 1)]}}
        write_route(path, page(f"{title} — Edit Online | ResumeNowOnline", description + " Browse and edit online for free.", path, body, [collection, crumb_schema, faq_schema]))


def article_page(slug, data):
    path = f"/career-advice/{slug}/"
    crumb, crumb_schema = breadcrumb([("Home", "/"), ("Career advice", "/career-advice/"), (data["title"], path)])
    toc = "".join(f'<a href="#section-{i}">{esc(title)}</a>' for i, (title, _) in enumerate(data["sections"], 1))
    sections = "".join(f'<section id="section-{i}"><h2>{esc(title)}</h2><p>{esc(copy)}</p></section>' for i, (title, copy) in enumerate(data["sections"], 1))
    faq, faq_schema = faq_markup(data["faq"])
    body = f'''<div class="seo-shell seo-article-shell">{crumb}<header class="seo-article-hero"><span class="seo-kicker">Resume guide · Updated {TODAY[:4]}</span><h1>{esc(data["title"])}</h1><p class="seo-lede">{esc(data["intro"])}</p></header><div class="seo-article-layout"><aside><strong>In this guide</strong>{toc}<a class="seo-side-cta" href="/resume-templates/">Choose a resume template →</a></aside><article class="seo-prose">{sections}<section class="seo-callout"><h2>Put the guidance into practice</h2><p>Choose one of 105 templates, edit it in the browser for free, and review the complete resume before downloading.</p><a class="button button--primary" href="/resume-templates/">Browse templates</a></section>{faq}</article></div></div>'''
    article_schema = {"@context": "https://schema.org", "@type": "Article", "headline": data["title"], "description": data["description"], "datePublished": TODAY, "dateModified": TODAY, "mainEntityOfPage": SITE + path, "author": {"@type": "Organization", "name": "ResumeNowOnline Editorial Team"}, "publisher": {"@type": "Organization", "name": "ResumeNowOnline", "url": SITE, "logo": {"@type": "ImageObject", "url": SITE + "/assets/brand/resume-now-mark-v2-512.png"}}}
    write_route(path, page(f'{data["title"]} | ResumeNowOnline', data["description"], path, body, [article_schema, crumb_schema, faq_schema]))


def generate_advice():
    for slug, data in GUIDES.items():
        article_page(slug, data)
    path = "/career-advice/"
    crumb, crumb_schema = breadcrumb([("Home", "/"), ("Career advice", path)])
    cards = "".join(f'<article class="seo-guide-card"><span>Resume guide</span><h2><a href="/career-advice/{slug}/">{esc(data["title"])}</a></h2><p>{esc(data["description"])}</p><a class="seo-text-link" href="/career-advice/{slug}/">Read the guide →</a></article>' for slug, data in GUIDES.items())
    body = f'''<div class="seo-shell">{crumb}<section class="seo-listing-hero"><span class="seo-kicker">Clear, practical advice</span><h1>Resume and Career Advice</h1><p class="seo-lede">Learn how to write, format, tailor, and review a resume with guidance designed for real applications.</p></section><section><div class="seo-guide-grid">{cards}</div></section><section class="seo-final-cta"><span>Ready to apply it?</span><h2>Start with a resume template.</h2><p>Edit free and pay $5 only for three PDF downloads.</p><a class="button button--light" href="/resume-templates/">Explore templates</a></section></div>'''
    write_route(path, page("Resume Writing and Career Advice | ResumeNowOnline", "Practical resume writing guides covering formats, summaries, skills, bullet points, ATS readability, length, and cover letters.", path, body, [{"@context": "https://schema.org", "@type": "CollectionPage", "name": "Resume and Career Advice", "url": SITE + path}, crumb_schema]))


def generate_jobs():
    hub_path = "/resume-examples/"
    hub_crumb, hub_schema = breadcrumb([("Home", "/"), ("Resume examples", hub_path)])
    hub_cards = []
    for slug, (title, skills, bullets) in JOBS.items():
        path = f"/resume-examples/{slug}/"
        role = title.replace(" Resume Example", "")
        desc = f"Use this {role.lower()} resume example to plan your summary, skills, and achievement-led work experience, then edit a matching template online."
        crumb, crumb_schema = breadcrumb([("Home", "/"), ("Resume examples", hub_path), (title, path)])
        bullets_html = "".join(f"<li>{esc(item)}</li>" for item in bullets)
        skills_html = "".join(f"<li>{esc(item)}</li>" for item in skills)
        faq, faq_schema = faq_markup([(f"What should a {role.lower()} resume include?", f"Lead with relevant {skills[0].lower()} experience, use clear achievement bullets, and tailor skills to the actual job description."), ("Can I copy these bullet points?", "Use them as structural examples, then replace every claim and number with evidence from your own experience."), ("Which format should I use?", "Reverse chronological format works for most candidates; a combination format can help foreground relevant projects or transferable skills.")])
        body = f'''<div class="seo-shell seo-article-shell">{crumb}<header class="seo-article-hero"><span class="seo-kicker">Role-specific resume example</span><h1>{esc(title)}</h1><p class="seo-lede">Build a focused {esc(role.lower())} resume by leading with relevant evidence, using the language of the role, and making your impact easy to scan.</p><div class="seo-actions"><a class="button button--primary" href="/resume-templates/">Choose a template</a><a class="button button--outline" href="#example">See example bullets</a></div></header><div class="seo-article-layout"><aside><strong>Core skills</strong><ul>{skills_html}</ul><a class="seo-side-cta" href="/career-advice/how-to-write-a-resume/">Resume writing guide →</a></aside><article class="seo-prose"><section><h2>How to structure a {esc(role.lower())} resume</h2><p>Use a concise headline and summary to establish your level and specialty. Follow with recent experience in reverse chronological order, giving the most space to work that resembles the target role. Add skills that can be verified by the bullets, projects, education, or certifications.</p></section><section id="example"><h2>{esc(role)} resume bullet examples</h2><p>Use the pattern and level of specificity below, but never copy facts that are not yours.</p><ul>{bullets_html}</ul></section><section><h2>Skills to consider</h2><p>Prioritize the skills requested by the employer when your own experience supports them.</p><ul>{skills_html}</ul></section><section><h2>Tailor the first half of the page</h2><p>Match the target title, reorder your strongest evidence, and use the employer’s normal terminology naturally. Remove unrelated details before reducing font size or margins.</p></section>{faq}</article></div></div>'''
        article_schema = {"@context": "https://schema.org", "@type": "Article", "headline": title, "description": desc, "datePublished": TODAY, "dateModified": TODAY, "mainEntityOfPage": SITE + path, "author": {"@type": "Organization", "name": "ResumeNowOnline Editorial Team"}, "publisher": {"@type": "Organization", "name": "ResumeNowOnline"}}
        write_route(path, page(f"{title}: Skills and Bullet Examples | ResumeNowOnline", desc, path, body, [article_schema, crumb_schema, faq_schema]))
        hub_cards.append(f'<article class="seo-guide-card"><span>Resume example</span><h2><a href="{path}">{esc(title)}</a></h2><p>Structure, skills, and achievement bullet examples for {esc(role.lower())} applications.</p><a class="seo-text-link" href="{path}">View example →</a></article>')
    hub_body = f'''<div class="seo-shell">{hub_crumb}<section class="seo-listing-hero"><span class="seo-kicker">Examples for 15 career paths</span><h1>Resume Examples by Job Title</h1><p class="seo-lede">See what to emphasize for your target role, then turn the guidance into a resume using any editable template.</p></section><section class="seo-editorial"><h2>Use examples as patterns, not scripts</h2><div><p>Good examples show the expected level of specificity, section order, and language for a role. Replace every claim, metric, and skill with evidence that is true for you.</p><p>After drafting, compare the first half of your resume with the job description. A reader should be able to see the connection without hunting for it.</p></div></section><div class="seo-guide-grid">{"".join(hub_cards)}</div></div>'''
    write_route(hub_path, page("Resume Examples by Job Title | ResumeNowOnline", "Browse resume examples for 15 popular job titles with role-specific skills, structure guidance, and achievement bullet examples.", hub_path, hub_body, [{"@context": "https://schema.org", "@type": "CollectionPage", "name": "Resume Examples by Job Title", "url": SITE + hub_path}, hub_schema]))


def generate_core_pages():
    core = {
        "/cv-maker/": ("Free CV Maker — Create a CV Online", "Create and edit a professional CV online for free. Choose a template and pay $5 only when you need three PDF downloads.", "Create a CV online, without starting from a blank page", "Choose a CV template, replace the sample content directly, and preview every included page. Editing is free; one $5 payment includes three PDF downloads.", ["Choose a layout that fits local expectations", "Write a concise profile for the target role", "Use evidence-led experience bullets", "Review all pages before exporting"]),
        "/cv-templates/": ("Free CV Templates to Edit Online", "Browse editable CV templates for international job applications. Customize online for free and get three PDF downloads for $5.", "CV templates for clear, professional applications", "In many countries, CV is the standard name for a concise employment document. These designs can be edited as a CV or resume, depending on the terminology used by the employer.", ["Professional and modern designs", "Complete multi-page preview", "Direct editing in your browser", "Transparent one-time download price"]),
        "/resume-format/": ("Resume Format Guide: Chronological, Functional, and Combination", "Compare chronological, functional, and combination resume formats and choose the structure that presents your experience clearly.", "Choose the right resume format for your story", "The layout should support the evidence. Reverse chronological is the clearest default, combination format can foreground relevant capabilities, and functional resumes require careful use because employers still expect a work history.", ["Chronological: best when recent experience is relevant", "Combination: useful for career changes and technical depth", "Functional: use sparingly and include clear dates", "Keep headings, spacing, and reading order consistent"]),
        "/cv-format/": ("CV Format Guide for International Applications", "Format a clear CV for international job applications with practical guidance on length, sections, typography, and regional expectations.", "A practical CV format for international roles", "Use the employer’s terminology and local convention. For most private-sector applications, a concise reverse-chronological CV with clear headings, relevant skills, and one or two readable pages is a strong default.", ["Check Letter vs A4 page size", "Follow local photo and personal-data norms", "Use reverse chronological experience", "Submit the requested PDF or DOCX format"]),
    }
    for path, (title, desc, heading, intro, points) in core.items():
        crumb, crumb_schema = breadcrumb([("Home", "/"), (title, path)])
        list_html = "".join(f"<li>{esc(p)}</li>" for p in points)
        templates = TEMPLATES[:12] if "format" not in path else [t for t in TEMPLATES if "ats" in template_tags(t)][:12]
        body = f'''<div class="seo-shell">{crumb}<section class="seo-listing-hero"><span class="seo-kicker">Free online editing</span><h1>{esc(heading)}</h1><p class="seo-lede">{esc(intro)}</p><div class="seo-actions"><a class="button button--primary" href="/resume-templates/">Choose a template</a><a class="button button--outline" href="/career-advice/how-to-write-a-resume/">Read the writing guide</a></div></section><section class="seo-copy-grid"><div><h2>Build around readable, relevant evidence</h2><p>{esc(desc)} Start with the sections a recruiter expects, tailor the document to the actual role, and keep the final text selectable.</p><ul class="seo-checks">{list_html}</ul></div><aside class="seo-note"><strong>ResumeNowOnline pricing</strong><p>All editing and previews are free. Three PDF downloads cost $5 as a one-time purchase.</p><a href="/pricing.html">See full pricing →</a></aside></section><section><div class="seo-section-heading"><span>Start with a design</span><h2>Recommended editable templates</h2></div><div class="seo-template-grid">{"".join(card(t) for t in templates)}</div></section></div>'''
        write_route(path, page(f"{title} | ResumeNowOnline", desc, path, body, [{"@context": "https://schema.org", "@type": "WebPage", "name": title, "description": desc, "url": SITE + path}, crumb_schema]))


def generate_support_files():
    routes = ["/", "/resume-templates/", "/resume-examples/", "/career-advice/", "/cv-maker/", "/cv-templates/", "/resume-format/", "/cv-format/", "/pricing.html", "/product.html", "/contact.html", "/privacy.html", "/terms.html", "/refunds.html"]
    routes += [f'/resume-templates/{t["slug"]}/' for t in TEMPLATES]
    routes += [f"/resume-templates/{slug}/" for slug in CATEGORIES if any(slug in template_tags(t) for t in TEMPLATES)]
    routes += [f"/career-advice/{slug}/" for slug in GUIDES]
    routes += [f"/resume-examples/{slug}/" for slug in JOBS]
    unique = list(dict.fromkeys(routes))
    urls = "".join(f"<url><loc>{SITE}{route}</loc><lastmod>{TODAY}</lastmod><changefreq>{'weekly' if route in ('/', '/resume-templates/') else 'monthly'}</changefreq><priority>{'1.0' if route == '/' else '0.9' if route == '/resume-templates/' else '0.8' if '/resume-templates/' in route else '0.7'}</priority></url>" for route in unique)
    (DIST / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>', encoding="utf-8")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /api/\nDisallow: /account.html\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    manifest = {"name": "ResumeNowOnline", "short_name": "ResumeNowOnline", "start_url": "/", "display": "standalone", "background_color": "#f5f5f7", "theme_color": "#0066cc", "icons": [{"src": "/assets/brand/resume-now-mark-v2-512.png", "sizes": "512x512", "type": "image/png"}]}
    (DIST / "site.webmanifest").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"SEO build: {len(unique)} canonical URLs, {len(TEMPLATES)} template pages")


def main():
    generate_catalog()
    generate_categories()
    generate_template_pages()
    generate_advice()
    generate_jobs()
    generate_core_pages()
    generate_support_files()


if __name__ == "__main__":
    main()
