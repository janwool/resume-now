#!/usr/bin/env python3
"""Generate crawlable SEO landing pages from the resume template catalog."""

from __future__ import annotations

import html
import json
import re
from datetime import date
from pathlib import Path

from role_guides import ROLE_GUIDES


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
SITE = "https://resume-now.online"
TODAY = date.today().isoformat()
ARTICLE_PUBLISHED = "2026-08-10"


def load_templates():
    source = (ROOT / "template-manifest.js").read_text(encoding="utf-8")
    payload = re.sub(r"^\s*window\.resumeTemplateManifest\s*=\s*", "", source)
    payload = re.sub(r";\s*$", "", payload)
    return json.loads(payload)


TEMPLATES = load_templates()
TEMPLATE_BY_ID = {template["id"]: template for template in TEMPLATES}


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
    "elegant": ("Elegant Resume Templates", "Refined resume templates with balanced typography, restrained details, and a polished professional finish."),
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
        "title": "What Is a CV vs Resume? Key Differences Explained",
        "description": "Learn what a CV is versus a resume, including differences in purpose, length, content, regional usage, and when to use each document.",
        "intro": "The meaning of CV and resume changes by country and industry. In the United States, a resume is usually a concise job application document, while an academic CV is a comprehensive record. In many other markets, CV is simply the common name for the document Americans call a resume.",
        "sections": [("Resume", "A resume is tailored to a specific role and usually runs one or two pages. It prioritizes relevant work, skills, education, and measurable achievements."), ("Academic CV", "An academic CV is much longer and can include research, publications, teaching, grants, conferences, awards, and professional service. It grows throughout a career."), ("Regional terminology", "Employers in the UK, Europe, parts of Asia, and other regions commonly ask for a CV when they expect a concise employment document. Always follow the language in the job posting."), ("How to decide", "Use a tailored resume for most private-sector applications in North America. Use a full academic CV for research, faculty, medical, or grant contexts. Elsewhere, use the employer’s preferred term and match local conventions.")],
        "faq": [("Can I use the same template?", "Yes for most job-search CVs. Academic CVs need a more document-like layout that can grow across many pages."), ("Is a CV always longer?", "Not internationally. A standard UK CV is commonly two pages, while a US academic CV can be much longer.")],
    },
    "resume-summary": {
        "title": "What Is a Resume Summary? How to Write One With Examples",
        "description": "Learn what a resume summary is and write a concise introduction that communicates your target role, experience, strengths, and evidence.",
        "intro": "A resume summary is a two-to-four-line introduction near the top of a resume. It should help a recruiter understand your fit before reading the work history. The useful version is specific, evidence-based, and tailored; the weak version is a stack of adjectives.",
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
    "what-is-a-resume": {
        "title": "What Is a Resume? Definition, Purpose, and Examples",
        "description": "Learn what a resume is, what employers expect it to include, how it differs from a CV, and which resume format to choose.",
        "intro": "A resume is a concise job-application document that presents the experience, skills, education, and achievements most relevant to a particular role. Its purpose is to help an employer decide whether to invite you to the next stage.",
        "sections": [
            ("What a resume includes", "Most resumes contain contact details, a headline or summary, work experience, education, and relevant skills. Projects, certifications, publications, volunteer work, or awards can be added when they strengthen the application."),
            ("What a resume is for", "A resume is not a full record of everything you have done. It is a tailored selection of evidence that shows you can perform the target role. The strongest version makes responsibilities, scale, and outcomes easy to find."),
            ("The three common resume formats", "Reverse chronological resumes lead with recent experience and are the clearest default. Combination resumes give more space to relevant capabilities before work history. Functional resumes emphasize skills but still need dates and credible evidence."),
            ("Resume vs CV", "In the United States, a resume is usually one or two pages while an academic CV is a comprehensive record of research, teaching, and publications. In many countries, CV is simply the normal term for a concise employment resume."),
            ("How to create one", "Start with the job description, select a readable template, write achievement-led experience, and tailor the first half of the document. Proofread the final PDF and confirm that its text can be selected in a logical order."),
        ],
        "faq": [("How long should a resume be?", "One page often works for students and early-career candidates. Two pages are appropriate when relevant experience needs the space."), ("Does a resume need a photo?", "Photo expectations vary by country. Photos are uncommon in US applications and may be discouraged."), ("Is a resume the same as a résumé?", "Yes. Resume and résumé refer to the same job-application document in English usage.")],
    },
    "how-to-build-a-resume-website": {
        "title": "How to Build a Resume Website: A Practical Guide",
        "description": "Plan and build a professional resume website with the right sections, domain, content, accessibility, mobile layout, and downloadable resume.",
        "intro": "A resume website gives employers a focused place to review your experience, work samples, and contact details. It works best as a clear complement to a tailored PDF resume, not as a replacement for every application document.",
        "sections": [
            ("Decide what the website must prove", "Choose a target role and identify the evidence a visitor needs: selected experience, two to five projects, measurable outcomes, skills, and an easy way to contact you. Remove unrelated material before choosing visual effects."),
            ("Use a simple page structure", "A practical sequence is introduction, selected experience, projects or case studies, skills, about, and contact. Put the strongest proof near the top and make each project understandable without opening another tab."),
            ("Choose a domain and platform", "Use a short domain based on your name when possible. A hosted portfolio builder is fastest; a static site gives more control. Whichever platform you choose, enable HTTPS and keep ownership of the domain and content."),
            ("Write for scanning and search", "Use one descriptive H1, clear section headings, concise project titles, meaningful link text, and a unique page title and description. Include role and specialty terms naturally, but do not repeat keywords without useful context."),
            ("Make it fast, accessible, and mobile", "Compress images, provide alt text, preserve color contrast, support keyboard navigation, and test on a phone. Avoid autoplay media, tiny text, and animations that hide essential information."),
            ("Connect the website to your resume", "Add the website URL to the contact area of your PDF resume and provide a downloadable resume on the site. Keep job titles, dates, and core facts consistent across both versions."),
        ],
        "faq": [("Do I need a resume website?", "No. It is most useful when projects, writing, design, code, research, or consulting work benefit from more context."), ("Can a website replace a PDF resume?", "Usually not. Many employers and application systems still request a PDF or DOCX file."), ("What should the domain name be?", "Your name or a short professional variation is usually the clearest choice.")],
    },
    "ai-resume-builder-guide": {
        "title": "AI Resume Builder Guide: Use AI Without Losing Your Voice",
        "description": "Learn how to use an AI resume builder for drafting and tailoring while keeping every claim accurate, specific, and recognizably yours.",
        "intro": "AI can help organize experience, suggest clearer phrasing, and compare a draft with a job description. It cannot verify facts, choose which achievements matter most, or replace your judgment about what is true.",
        "sections": [
            ("Start from verified facts", "Collect job titles, dates, responsibilities, outcomes, tools, and metrics before asking for a draft. Do not let a model invent numbers, customers, certifications, or scope."),
            ("Give the AI a narrow task", "Ask for alternatives to one summary or bullet rather than a complete fictional resume. Provide the target role and real context, then compare the suggestions with your original evidence."),
            ("Keep the language specific", "Replace generic phrases such as results-driven or dynamic professional with the actual domain, level, work, and outcome. Read every sentence aloud and remove wording you would not use in an interview."),
            ("Tailor without keyword stuffing", "Use terminology from the job description when it accurately matches your experience. Reorder relevant evidence, but do not paste long keyword lists or hide terms in the document."),
            ("Review privacy and accuracy", "Avoid entering confidential client data, private financial information, or personal identifiers into tools without understanding their data policy. Verify spelling, dates, metrics, and links before exporting."),
        ],
        "faq": [("Can AI write my entire resume?", "It can draft text, but you must supply and verify the evidence. A polished fictional claim is still false."), ("Will AI make a resume ATS-friendly?", "AI can help with headings and terminology, but no tool can guarantee how every employer's system will process a file."), ("Does ResumeNowOnline use AI?", "The current ResumeNowOnline editor focuses on editable templates and does not claim automatic AI writing.")],
    },
}


def esc(value):
    return html.escape(str(value), quote=True)


def branded_title(value):
    suffix = " | ResumeNowOnline"
    return value + suffix if len(value) + len(suffix) <= 68 else value


def write_route(route, content):
    folder = DIST if route == "/" else DIST / route.strip("/")
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "index.html").write_text(content, encoding="utf-8")


def schema_json(data):
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def header():
    return """<header class=\"seo-nav\"><a class=\"brand\" href=\"/\"><img class=\"brand-icon\" src=\"/assets/brand/resume-now-mark-v2-64.png\" alt=\"\" width=\"25\" height=\"25\">ResumeNowOnline</a><nav aria-label=\"Main navigation\"><a href=\"/resume-builder/\">Resume builder</a><a href=\"/resume-templates/\">Templates</a><a href=\"/resume-examples/\">Examples</a><a href=\"/ats-resume-checker/\">ATS checker</a><a href=\"/career-advice/\">Guides</a></nav><a class=\"button button--primary button--small\" href=\"/builder.html\">Create free</a></header>"""


def footer():
    return """<footer class=\"seo-footer\"><div><a class=\"brand\" href=\"/\"><img class=\"brand-icon\" src=\"/assets/brand/resume-now-mark-v2-64.png\" alt=\"\" width=\"25\" height=\"25\">ResumeNowOnline</a><p>Create, edit, and download a complete resume online for free.</p></div><div><strong>Build</strong><a href=\"/resume-builder/\">Free resume builder</a><a href=\"/resume-templates/\">Resume templates</a><a href=\"/cv-maker/\">CV maker</a><a href=\"/ats-resume-checker/\">ATS resume checker</a></div><div><strong>Learn</strong><a href=\"/career-advice/how-to-write-a-resume/\">How to write a resume</a><a href=\"/career-advice/resume-summary/\">Resume summaries</a><a href=\"/resume-format/\">Resume formats</a><a href=\"/career-advice/cv-vs-resume/\">CV vs resume</a></div><div><strong>Company</strong><a href=\"/pricing.html\">Free access</a><a href=\"/contact.html\">Contact</a><a href=\"/privacy.html\">Privacy</a><a href=\"/terms.html\">Terms</a></div></footer>"""


def page(title, description, path, body, schemas, image="/assets/template-previews/template-001.jpg", robots="index,follow", extra_body=""):
    canonical = SITE + path
    global_schemas = [
        {"@context": "https://schema.org", "@type": "Organization", "@id": SITE + "/#organization", "name": "ResumeNowOnline", "url": SITE + "/", "logo": SITE + "/assets/brand/resume-now-mark-v2-512.png", "email": "support@resume-now.online"},
        {"@context": "https://schema.org", "@type": "WebSite", "@id": SITE + "/#website", "name": "ResumeNowOnline", "url": SITE + "/", "publisher": {"@id": SITE + "/#organization"}, "inLanguage": "en"},
    ]
    schema_blocks = "".join(f'<script type="application/ld+json">{schema_json(item)}</script>' for item in [*global_schemas, *schemas])
    return f"""<!doctype html><html lang=\"en\"><head><meta charset=\"UTF-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>{esc(title)}</title><meta name=\"description\" content=\"{esc(description)}\"><meta name=\"robots\" content=\"{robots}\"><meta name=\"author\" content=\"ResumeNowOnline Editorial Team\"><meta name=\"theme-color\" content=\"#f5f5f7\"><link rel=\"canonical\" href=\"{canonical}\"><meta property=\"og:type\" content=\"website\"><meta property=\"og:site_name\" content=\"ResumeNowOnline\"><meta property=\"og:title\" content=\"{esc(title)}\"><meta property=\"og:description\" content=\"{esc(description)}\"><meta property=\"og:url\" content=\"{canonical}\"><meta property=\"og:image\" content=\"{SITE}{image}\"><meta property=\"og:image:width\" content=\"1200\"><meta property=\"og:image:height\" content=\"630\"><meta name=\"twitter:card\" content=\"summary_large_image\"><meta name=\"twitter:title\" content=\"{esc(title)}\"><meta name=\"twitter:description\" content=\"{esc(description)}\"><meta name=\"twitter:image\" content=\"{SITE}{image}\"><link rel=\"icon\" type=\"image/png\" sizes=\"32x32\" href=\"/assets/brand/favicon-v2-32.png\"><link rel=\"apple-touch-icon\" href=\"/assets/brand/apple-touch-icon-v2.png\"><link rel=\"stylesheet\" href=\"/styles.css?v=43\">{schema_blocks}</head><body class=\"seo-page\">{header()}<main>{body}</main>{footer()}{extra_body}</body></html>"""


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
        "elegant": ("elegant", "refined", "luxury", "sophisticated", "heritage"),
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
        desc = f'Customize the {template["name"]} online for free. Edit every section, preview every page, and download your finished resume as a PDF for free.'
        path = f'/resume-templates/{template["slug"]}/'
        crumb, crumb_schema = breadcrumb([("Home", "/"), ("Resume templates", "/resume-templates/"), (template["name"], path)])
        pages = sorted((ROOT / "assets" / "template-pages" / template["id"]).glob("page-*.jpg"))
        previews = pages or [ROOT / template["preview"]]
        gallery = "".join(f'<figure><img src="/{esc(p.relative_to(ROOT).as_posix())}" alt="{esc(template["name"])} page {i}" loading="lazy"><figcaption>Page {i}</figcaption></figure>' for i, p in enumerate(previews, 1))
        tags = sorted(template_tags(template))
        category_links = "".join(f'<a href="/resume-templates/{tag}/">{esc(tag.replace("-", " ").title())}</a>' for tag in tags if tag in CATEGORIES)
        faq, faq_schema = faq_markup([("Is this resume template free?", "Yes. You can open the template, edit its content, and download the finished PDF without paying."), ("Can I download the resume for free?", "Yes. PDF export is free and does not require an account or payment."), ("Can I edit the whole resume?", "Yes. Select text and supported elements directly on the resume canvas; available controls appear beside the document."), ("Does the editor preserve every template page?", "Yes. The editor loads the template’s available pages and keeps its visual layout while you make changes.")])
        product_schema = {"@context": "https://schema.org", "@type": "SoftwareApplication", "name": template["name"], "applicationCategory": "BusinessApplication", "operatingSystem": "Web", "description": desc, "url": SITE + path, "image": SITE + "/" + template["preview"], "offers": {"@type": "Offer", "name": "Free resume editing and PDF download", "price": "0", "priceCurrency": "USD"}, "publisher": {"@type": "Organization", "name": "ResumeNowOnline", "url": SITE}}
        body = f'''<div class="seo-shell">{crumb}<section class="seo-template-hero"><div><span class="seo-kicker">Free to edit and download</span><h1>{esc(template["name"])}</h1><p class="seo-lede">{esc(template["subtitle"])}. Keep the original visual design, replace the sample content directly on the resume, and download the finished PDF for free.</p><div class="seo-actions"><a class="button button--primary" href="/builder.html?template={esc(template["id"])}">Use this template</a><a class="button button--outline" href="#preview">Preview all pages</a></div><ul class="seo-checks"><li>Edit the complete resume online</li><li>All available template pages included</li><li>Free PDF download without an account</li></ul></div><div class="seo-hero-preview"><img src="/{esc(template["preview"])}" alt="{esc(template["name"])} full preview"></div></section><section class="seo-copy-grid"><div><span class="seo-kicker">Designed for real applications</span><h2>A structured starting point, ready for your experience</h2><p>This {esc(', '.join(tags[:3]))} resume template gives your name, profile, experience, education, and skills a deliberate visual hierarchy. Replace the example text with evidence from your own work and tailor the first half of the document to the role.</p><p>For the cleanest result, keep bullets concise, use consistent dates, and remove any section that does not strengthen the application. Review every page before exporting.</p><div class="seo-tag-list">{category_links}</div></div><aside class="seo-note"><strong>Free from start to finish</strong><p>Choose a template, edit every supported element, preview all pages, and download the PDF without a paywall.</p><a href="/resume-builder/">Open the free builder →</a></aside></section><section class="seo-preview-section" id="preview"><div class="seo-section-heading"><span>Template preview</span><h2>See every included page</h2><p>The editor opens the same template shown here—not just its colors.</p></div><div class="seo-page-gallery">{gallery}</div></section>{faq}<section class="seo-final-cta"><span>Ready to make it yours?</span><h2>Edit and download this resume for free.</h2><p>No account, card, or download credits required.</p><a class="button button--light" href="/builder.html?template={esc(template["id"])}">Start editing</a></section></div>'''
        write_route(path, page(title, desc, path, body, [product_schema, crumb_schema, faq_schema], "/" + template["preview"]))


def generate_catalog():
    path = "/resume-templates/"
    crumb, crumb_schema = breadcrumb([("Home", "/"), ("Resume templates", path)])
    category_nav = "".join(f'<a href="/resume-templates/{slug}/">{esc(title.replace(" Resume Templates", ""))}</a>' for slug, (title, _) in CATEGORIES.items())
    body = f'''<div class="seo-shell">{crumb}<section class="seo-listing-hero"><span class="seo-kicker">105 editable designs</span><h1>Free Resume Templates to Edit Online</h1><p class="seo-lede">Browse professional resume templates, open the complete design in our free resume builder, edit every included page, and download your finished PDF for free.</p><div class="seo-actions"><a class="button button--primary" href="/resume-builder/">Build my resume free</a><a class="button button--outline" href="#templates">Browse all templates</a></div></section><nav class="seo-chip-nav" aria-label="Resume template categories">{category_nav}</nav><section class="seo-editorial"><h2>Choose a resume template for the way you want to be read</h2><div><p>A strong resume format makes relevant evidence easy to find. Start with a simple or ATS-friendly template for application portals, a professional layout for broad business roles, or a creative design when visual judgment is part of the work.</p><p>Every design below opens as the actual template in the editor. You can replace sample text across all included pages, upload a photo where supported, preview the finished resume, and export a PDF without entering payment details.</p></div></section><section class="seo-copy-grid"><div><span class="seo-kicker">Free resume templates</span><h2>Free to customize and download.</h2><p>Choosing a template, editing the complete resume, previewing every page, and exporting the finished PDF are free. There is no account requirement or download-credit limit.</p><p>Use the browser print dialog to save the document as a PDF when it is ready. Review every page first so dates, links, and page endings appear exactly as intended.</p></div><aside class="seo-note"><strong>Looking for the right format?</strong><p>Compare chronological, combination, and functional resume formats before choosing a design.</p><a href="/resume-format/">Read the resume format guide →</a></aside></section><section id="templates"><div class="seo-section-heading"><span>Complete collection</span><h2>All 105 resume templates</h2><p>Filter by ATS-friendly, professional, modern, minimal, creative, executive, student, one-page, two-column, or elegant styles.</p></div><div class="seo-template-grid">{"".join(card(t) for t in TEMPLATES)}</div></section><section class="seo-final-cta"><span>Free online editor</span><h2>Choose a template and make it yours.</h2><p>Edit, preview, and download the complete resume for free.</p><a class="button button--light" href="/resume-builder/">Open the resume builder</a></section></div>'''
    collection = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Free Resume Templates", "description": "105 editable resume templates", "url": SITE + path, "mainEntity": {"@type": "ItemList", "numberOfItems": len(TEMPLATES), "itemListElement": [{"@type": "ListItem", "position": i, "url": f'{SITE}/resume-templates/{t["slug"]}/', "name": t["name"]} for i, t in enumerate(TEMPLATES, 1)]}}
    write_route(path, page("Free Resume Templates: 105 Editable Designs | ResumeNowOnline", "Browse 105 free resume templates for ATS, professional, modern, simple, and creative applications. Edit every page and download your PDF for free.", path, body, [collection, crumb_schema]))


def generate_categories():
    for slug, (title, description) in CATEGORIES.items():
        selected = [t for t in TEMPLATES if slug in template_tags(t)]
        if not selected:
            continue
        path = f"/resume-templates/{slug}/"
        crumb, crumb_schema = breadcrumb([("Home", "/"), ("Resume templates", "/resume-templates/"), (title, path)])
        faq, faq_schema = faq_markup([("Can I edit these templates for free?", "Yes. Editing, previewing, and PDF downloads are free."), ("Do I need an account to download?", "No. You can save your finished resume as a PDF without signing in."), ("Which template should I choose?", "Choose the layout that gives your most relevant experience enough room and matches the expectations of your target role.")])
        body = f'''<div class="seo-shell">{crumb}<section class="seo-listing-hero"><span class="seo-kicker">Curated collection · {len(selected)} designs</span><h1>{esc(title)}</h1><p class="seo-lede">{esc(description)} Edit every section and download the finished PDF for free.</p><div class="seo-actions"><a class="button button--primary" href="#templates">Choose a template</a><a class="button button--outline" href="/resume-templates/">View all 105</a></div></section><section class="seo-editorial"><h2>When this resume style works best</h2><div><p>{esc(description)} The right choice still depends on your content: prioritize readable text, consistent headings, and enough space for concrete achievements.</p><p>Start with the original design, replace the sample content directly, and keep only the sections that help a recruiter assess your fit. For automated application portals, test the exported PDF’s selectable text and reading order.</p></div></section><section id="templates"><div class="seo-template-grid">{"".join(card(t) for t in selected)}</div></section>{faq}</div>'''
        collection = {"@context": "https://schema.org", "@type": "CollectionPage", "name": title, "description": description, "url": SITE + path, "mainEntity": {"@type": "ItemList", "numberOfItems": len(selected), "itemListElement": [{"@type": "ListItem", "position": i, "url": f'{SITE}/resume-templates/{t["slug"]}/', "name": t["name"]} for i, t in enumerate(selected, 1)]}}
        write_route(path, page(f"{title} — Edit Online | ResumeNowOnline", description + " Browse and edit online for free.", path, body, [collection, crumb_schema, faq_schema]))


def article_page(slug, data):
    path = f"/career-advice/{slug}/"
    crumb, crumb_schema = breadcrumb([("Home", "/"), ("Career advice", "/career-advice/"), (data["title"], path)])
    toc = "".join(f'<a href="#section-{i}">{esc(title)}</a>' for i, (title, _) in enumerate(data["sections"], 1))
    sections = "".join(f'<section id="section-{i}"><h2>{esc(title)}</h2><p>{esc(copy)}</p></section>' for i, (title, copy) in enumerate(data["sections"], 1))
    faq, faq_schema = faq_markup(data["faq"])
    body = f'''<div class="seo-shell seo-article-shell">{crumb}<header class="seo-article-hero"><span class="seo-kicker">Resume guide · Updated {TODAY[:4]}</span><h1>{esc(data["title"])}</h1><p class="seo-lede">{esc(data["intro"])}</p></header><div class="seo-article-layout"><aside><strong>In this guide</strong>{toc}<a class="seo-side-cta" href="/resume-templates/">Choose a resume template →</a></aside><article class="seo-prose">{sections}<section class="seo-callout"><h2>Put the guidance into practice</h2><p>Choose one of 105 templates, edit it in the browser for free, and review the complete resume before downloading.</p><a class="button button--primary" href="/resume-templates/">Browse templates</a></section>{faq}</article></div></div>'''
    article_schema = {"@context": "https://schema.org", "@type": "Article", "headline": data["title"], "description": data["description"], "datePublished": ARTICLE_PUBLISHED, "dateModified": TODAY, "mainEntityOfPage": SITE + path, "author": {"@type": "Organization", "name": "ResumeNowOnline Editorial Team"}, "publisher": {"@id": SITE + "/#organization"}}
    write_route(path, page(branded_title(data["title"]), data["description"], path, body, [article_schema, crumb_schema, faq_schema]))


def generate_advice():
    for slug, data in GUIDES.items():
        article_page(slug, data)
    path = "/career-advice/"
    crumb, crumb_schema = breadcrumb([("Home", "/"), ("Career advice", path)])
    cards = "".join(f'<article class="seo-guide-card"><span>Resume guide</span><h2><a href="/career-advice/{slug}/">{esc(data["title"])}</a></h2><p>{esc(data["description"])}</p><a class="seo-text-link" href="/career-advice/{slug}/">Read the guide →</a></article>' for slug, data in GUIDES.items())
    body = f'''<div class="seo-shell">{crumb}<section class="seo-listing-hero"><span class="seo-kicker">Clear, practical advice</span><h1>Resume and Career Advice</h1><p class="seo-lede">Learn how to write, format, tailor, and review a resume with guidance designed for real applications.</p></section><section class="seo-profession-feature"><div><span class="seo-kicker">Guides by profession</span><h2>Write for the work you actually do.</h2><p>Recruiters look for different evidence in nursing, software, finance, sales, education, logistics, and skilled trades. Browse role-specific guidance for section order, skills, metrics, and achievement bullets.</p><a class="button button--primary" href="/career-advice/resume-guides-by-profession/">Browse profession guides</a></div><div class="seo-industry-list"><a href="/career-advice/resume-guides-by-profession/#technology">Technology</a><a href="/career-advice/resume-guides-by-profession/#healthcare">Healthcare</a><a href="/career-advice/resume-guides-by-profession/#finance">Finance</a><a href="/career-advice/resume-guides-by-profession/#education">Education</a><a href="/career-advice/resume-guides-by-profession/#logistics-and-transportation">Logistics</a><a href="/career-advice/resume-guides-by-profession/#skilled-trades">Skilled trades</a></div></section><section><div class="seo-section-heading"><span>Resume fundamentals</span><h2>Guidance for every application</h2></div><div class="seo-guide-grid">{cards}</div></section><section class="seo-final-cta"><span>Ready to apply it?</span><h2>Start with a resume template.</h2><p>Edit every page and download the finished PDF for free.</p><a class="button button--light" href="/resume-templates/">Explore templates</a></section></div>'''
    write_route(path, page("Resume Writing and Career Advice | ResumeNowOnline", "Practical resume writing guides covering formats, summaries, skills, bullet points, ATS readability, length, and cover letters.", path, body, [{"@context": "https://schema.org", "@type": "CollectionPage", "name": "Resume and Career Advice", "url": SITE + path}, crumb_schema]))


def compact_template_card(template):
    return f'''<article class="seo-role-template"><a href="/resume-templates/{esc(template["slug"])}/"><img src="/{esc(template["preview"])}" alt="{esc(template["name"])} preview" loading="lazy" width="180" height="240"></a><div><strong>{esc(template["name"].replace(" Resume Template", ""))}</strong><a href="/builder.html?template={esc(template["id"])}">Use this template →</a></div></article>'''


def generate_profession_hub():
    path = "/career-advice/resume-guides-by-profession/"
    crumb, crumb_schema = breadcrumb([("Home", "/"), ("Career advice", "/career-advice/"), ("Resume guides by profession", path)])
    industries = {}
    for slug, data in ROLE_GUIDES.items():
        industries.setdefault(data["industry"], []).append((slug, data))
    industry_notes = {
        "Technology": "Show systems, tools, scale, and the decisions behind reliable delivery.",
        "Product and Program Management": "Connect prioritization, coordination, risk, and tradeoffs with measurable outcomes.",
        "Finance": "Make accuracy, scope, controls, forecasts, and decision support easy to verify.",
        "Marketing and Sales": "Tie audience and customer work to qualified demand, revenue, retention, or account growth.",
        "Human Resources": "Show workforce scope, sound judgment, hiring or people-program ownership, and outcomes without exposing private employee data.",
        "Administration and Operations": "Demonstrate judgment, organization, discretion, and the volume of work kept on track.",
        "Customer Service": "Balance service volume and speed with quality, resolution, and customer outcomes.",
        "Creative": "Explain the system, brief, collaboration, and production impact behind the portfolio work.",
        "Education": "Show subject expertise, learning outcomes, classroom practice, and community contribution.",
        "Healthcare": "Lead with active credentials, clinical setting, patient population, safety, and verified scope.",
        "Legal": "Make practice-area experience, deadlines, research, document quality, jurisdiction, and confidentiality easy to evaluate.",
        "Retail": "Connect customer service and product knowledge with sales contribution, transaction accuracy, merchandising, and store reliability.",
        "Early Career": "Translate coursework, projects, part-time work, and campus leadership into useful evidence.",
        "Engineering and Construction": "State discipline, project scale, requirements, safety, verification, schedule, and cost.",
        "Logistics and Transportation": "Make licenses, equipment, throughput, accuracy, safety, and service reliability visible.",
        "Skilled Trades": "Put license level, systems, safe workmanship, troubleshooting, and project context near the top.",
        "Hospitality": "Show the service setting, pace, accuracy, guest experience, sales judgment, and teamwork.",
    }
    sections = []
    item_list = []
    position = 0
    for industry, entries in industries.items():
        anchor = re.sub(r"[^a-z0-9]+", "-", industry.lower()).strip("-")
        cards = []
        for slug, data in entries:
            position += 1
            url = f"/resume-examples/{slug}/"
            cards.append(f'''<article class="seo-profession-card"><span>{esc(data["industry"])}</span><h3><a href="{url}">{esc(data["role"])} resume guide</a></h3><p>{esc(data["priorities"][0])}, {esc(data["priorities"][1].lower())}, and evidence that fits the role.</p><a href="{url}">How to write it →</a></article>''')
            item_list.append({"@type": "ListItem", "position": position, "url": SITE + url, "name": f'{data["role"]} resume guide'})
        sections.append(f'''<section class="seo-industry-section" id="{anchor}"><div class="seo-industry-heading"><span>{esc(industry)}</span><h2>{esc(industry)} resume guides</h2><p>{esc(industry_notes[industry])}</p></div><div class="seo-profession-grid">{"".join(cards)}</div></section>''')
    chips = "".join(f'<a href="#{re.sub(r"[^a-z0-9]+", "-", industry.lower()).strip("-")}">{esc(industry)}</a>' for industry in industries)
    body = f'''<div class="seo-shell">{crumb}<section class="seo-listing-hero"><span class="seo-kicker">Resume advice by occupation</span><h1>How to Write a Resume for Your Profession</h1><p class="seo-lede">Choose your field to see the experience, skills, metrics, credentials, and achievement examples recruiters expect in that kind of resume.</p></section><nav class="seo-chip-nav seo-chip-nav--wrap" aria-label="Industries">{chips}</nav><section class="seo-editorial"><h2>Use the guide as a framework.</h2><div><p>Each profession values different evidence. A nurse needs clear licensure and clinical scope. A software engineer needs systems and production outcomes. A sales representative needs quota, segment, and pipeline context.</p><p>Keep every claim true. Replace the sample numbers and bullets with your own work, then tailor the first half of the resume to the job description.</p></div></section>{"".join(sections)}<section class="seo-final-cta"><span>Free resume builder</span><h2>Turn the guidance into a finished resume.</h2><p>Choose a template, edit every page, and download the PDF for free.</p><a class="button button--light" href="/resume-templates/">Choose a template</a></section></div>'''
    schemas = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": "Resume Guides by Profession", "description": "Role-specific resume writing guides covering skills, metrics, credentials, summaries, and achievement examples.", "url": SITE + path}, {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": item_list}, crumb_schema]
    write_route(path, page("Resume Guides by Profession | ResumeNowOnline", "Learn how to write a resume for technology, healthcare, finance, education, logistics, skilled trades, hospitality, and more.", path, body, schemas))


def generate_jobs():
    hub_path = "/resume-examples/"
    hub_crumb, hub_schema = breadcrumb([("Home", "/"), ("Resume examples", hub_path)])
    hub_cards = []
    item_list = []
    for position, (slug, data) in enumerate(ROLE_GUIDES.items(), 1):
        path = f"/resume-examples/{slug}/"
        role = data["role"]
        title = f"How to Write a {role} Resume"
        desc = f"Write a stronger {role.lower()} resume with role-specific structure, skills, metrics, summary guidance, and achievement bullet examples."
        crumb, crumb_schema = breadcrumb([("Home", "/"), ("Resume examples", hub_path), (title, path)])
        priorities = "".join(f'<div><i>{index}</i><strong>{esc(item)}</strong></div>' for index, item in enumerate(data["priorities"], 1))
        skills = "".join(f"<li>{esc(item)}</li>" for item in data["skills"])
        metrics = "".join(f'<div><strong>{esc(label)}</strong><p>{esc(copy.capitalize())}</p></div>' for label, copy in data["metrics"])
        bullets = "".join(f"<li>{esc(item)}</li>" for item in data["bullets"])
        recruiter_list = "".join(f"<li>{esc(item)}</li>" for item in data["priorities"])
        mistake_list = "".join(f"<li>{esc(item)}</li>" for item in data["mistakes"])
        recommended = [TEMPLATE_BY_ID[item] for item in data["templates"] if item in TEMPLATE_BY_ID]
        template_cards = "".join(compact_template_card(template) for template in recommended)
        hero_template = recommended[0] if recommended else TEMPLATES[3]
        faq_items = [
            (f"What should a {role.lower()} resume include?", f"Lead with {data['priorities'][0].lower()}, show relevant {data['skills'][0].lower()} experience in context, and use achievement bullets that explain scope and outcome."),
            (f"What skills belong on a {role.lower()} resume?", f"Prioritize skills from the target job that you can prove in experience, projects, education, or credentials. Useful examples include {', '.join(item.lower() for item in data['skills'][:4])}."),
            ("Can I use the example numbers and bullet points?", "No. The examples demonstrate structure and specificity. Replace every action, number, tool, and result with evidence that is true for your own work."),
            ("Which resume format should I use?", "Reverse chronological format works for most candidates. Use a combination format when projects or transferable skills need more emphasis, but keep dates and work history clear."),
        ]
        faq, faq_schema = faq_markup(faq_items)
        toc = "".join(f'<a href="#{anchor}">{label}</a>' for anchor, label in [("recruiter-priorities", "What recruiters need"), ("summary", "Resume summary"), ("structure", "Resume structure"), ("skills", "Skills to include"), ("metrics", "Useful metrics"), ("examples", "Bullet examples"), ("mistakes", "Common mistakes"), ("templates", "Recommended templates")])
        body = f'''<div class="seo-shell seo-role-shell">{crumb}<header class="seo-role-hero"><div><span class="seo-kicker">{esc(data["industry"])} resume guide · Updated {TODAY[:4]}</span><h1>{esc(title)}</h1><p class="seo-lede">{esc(data["intro"])}</p><div class="seo-actions"><a class="button button--primary" href="/builder.html?template={esc(hero_template["id"])}">Build this resume free</a><a class="button button--outline" href="#examples">See bullet examples</a></div></div><a class="seo-role-preview" href="/resume-templates/{esc(hero_template["slug"])}/" aria-label="View recommended {esc(hero_template["name"])}"><img src="/{esc(hero_template["preview"])}" alt="{esc(hero_template["name"])} preview" width="360" height="510"></a></header><div class="seo-role-layout"><aside><strong>On this page</strong>{toc}<a class="seo-side-cta" href="/career-advice/resume-guides-by-profession/">All profession guides →</a></aside><article class="seo-role-article"><section class="seo-role-card" id="recruiter-priorities"><div class="seo-role-heading"><span>Start with the hiring decision</span><h2>What recruiters need to see</h2><p>The first half of the page should establish role fit before the reader reaches older experience.</p></div><div class="seo-priority-grid">{priorities}</div></section><section class="seo-role-card" id="summary"><div class="seo-role-heading"><span>Example</span><h2>{esc(role)} resume summary</h2><p>Use this as a pattern for level, scope, specialty, and evidence. Do not copy facts that are not yours.</p></div><blockquote class="seo-summary-example">{esc(data["summary"])}</blockquote></section><section class="seo-role-card" id="structure"><div class="seo-role-heading"><span>Recommended order</span><h2>How to structure the resume</h2></div><ol class="seo-structure-list"><li><strong>Contact details and target title.</strong> Use the normal title from the job posting and provide working contact links.</li><li><strong>Focused summary.</strong> Establish your level, setting, specialty, and one representative outcome.</li><li><strong>Recent relevant experience.</strong> Use reverse chronological order and give the most space to work that resembles the target role.</li><li><strong>Role-specific skills.</strong> Keep a scannable list, then prove the important skills in bullets.</li><li><strong>Education and credentials.</strong> {esc(data["credentials"])}</li></ol></section><section class="seo-role-card" id="skills"><div class="seo-role-heading"><span>Use only what you can support</span><h2>Skills to include</h2><p>Match the employer's terminology when it accurately describes your experience.</p></div><ul class="seo-skill-chips">{skills}</ul></section><section class="seo-role-card" id="metrics"><div class="seo-role-heading"><span>Evidence ideas</span><h2>Useful metrics for a {esc(role.lower())} resume</h2><p>Numbers should clarify scope or change. They do not need to be revenue figures.</p></div><div class="seo-metric-grid">{metrics}</div></section><section class="seo-role-card" id="examples"><div class="seo-role-heading"><span>Writing patterns</span><h2>{esc(role)} resume bullet examples</h2><p>Adapt the action, context, and result to your own verified work.</p></div><ul class="seo-bullet-examples">{bullets}</ul></section><section class="seo-role-compare" id="mistakes"><div><span class="seo-positive">Look for</span><h2>Strong signals</h2><ul>{recruiter_list}</ul></div><div><span class="seo-negative">Avoid</span><h2>Common mistakes</h2><ul>{mistake_list}</ul></div></section><section class="seo-role-card" id="templates"><div class="seo-role-heading"><span>Free to edit and download</span><h2>Recommended resume templates</h2><p>These layouts keep the hierarchy clear while giving role-specific evidence enough room.</p></div><div class="seo-role-template-grid">{template_cards}</div></section>{faq}<section class="seo-final-cta seo-role-cta"><span>Build your {esc(role.lower())} resume</span><h2>Start with a complete template.</h2><p>Edit every page and download the finished PDF for free.</p><a class="button button--light" href="/builder.html?template={esc(hero_template["id"])}">Create my resume</a></section></article></div></div>'''
        article_schema = {"@context": "https://schema.org", "@type": "Article", "headline": title, "description": desc, "datePublished": ARTICLE_PUBLISHED, "dateModified": TODAY, "mainEntityOfPage": SITE + path, "author": {"@type": "Organization", "name": "ResumeNowOnline Editorial Team"}, "publisher": {"@id": SITE + "/#organization"}}
        howto_schema = {"@context": "https://schema.org", "@type": "HowTo", "name": title, "description": desc, "step": [{"@type": "HowToStep", "position": index, "name": name, "text": text} for index, (name, text) in enumerate([("Choose a target", f"Use the normal {role.lower()} title from the job posting."), ("Write a focused summary", "State your level, setting, specialty, and one verified result."), ("Add relevant experience", "Use reverse chronological order and achievement-led bullets."), ("Select skills", "Include relevant skills you can support with evidence."), ("Review and export", "Check facts, reading order, page endings, and links before downloading the PDF.")], 1)]}
        write_route(path, page(branded_title(f"{role} Resume Guide and Examples"), desc, path, body, [article_schema, howto_schema, crumb_schema, faq_schema], image="/" + hero_template["preview"]))
        hub_cards.append(f'<article class="seo-guide-card"><span>{esc(data["industry"])}</span><h2><a href="{path}">{esc(role)} resume guide</a></h2><p>Role-specific structure, skills, metrics, summary guidance, and achievement examples.</p><a class="seo-text-link" href="{path}">Read the guide →</a></article>')
        item_list.append({"@type": "ListItem", "position": position, "url": SITE + path, "name": f"{role} resume guide"})
    hub_body = f'''<div class="seo-shell">{hub_crumb}<section class="seo-listing-hero"><span class="seo-kicker">Guides for {len(ROLE_GUIDES)} career paths</span><h1>Resume Examples by Job Title</h1><p class="seo-lede">See what recruiters need from your profession, then use role-specific summaries, skills, metrics, and achievement patterns to write your own resume.</p></section><section class="seo-editorial"><h2>Use examples as patterns, not scripts.</h2><div><p>Each guide explains the evidence that matters for the role. Replace every sample action, metric, credential, and result with facts from your own work.</p><p>After drafting, compare the first half of the resume with the job description. The connection should be clear without keyword stuffing.</p></div></section><div class="seo-guide-grid">{"".join(hub_cards)}</div><section class="seo-final-cta"><span>Free from start to finish</span><h2>Choose a template and write your version.</h2><p>Edit every page and download the finished PDF for free.</p><a class="button button--light" href="/resume-templates/">Browse templates</a></section></div>'''
    list_schema = {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": item_list}
    write_route(hub_path, page("Resume Examples and Writing Guides by Job | ResumeNowOnline", f"Browse resume examples and writing guides for {len(ROLE_GUIDES)} job titles with role-specific skills, metrics, summaries, and achievement bullets.", hub_path, hub_body, [{"@context": "https://schema.org", "@type": "CollectionPage", "name": "Resume Examples by Job Title", "url": SITE + hub_path}, list_schema, hub_schema]))


def generate_core_pages():
    core = {
        "/cv-maker/": ("Free CV Maker — Create a CV Online", "Create, edit, and download a professional CV online for free using a complete editable template.", "Create a CV online, without starting from a blank page", "Choose a CV template, replace the sample content directly, preview every included page, and download the finished PDF for free.", ["Choose a layout that fits local expectations", "Write a concise profile for the target role", "Use evidence-led experience bullets", "Review all pages before exporting"]),
        "/cv-templates/": ("Free CV Templates to Edit Online", "Browse editable CV templates for international job applications. Customize every page and download your PDF for free.", "CV templates for clear, professional applications", "In many countries, CV is the standard name for a concise employment document. These designs can be edited as a CV or resume, depending on the terminology used by the employer.", ["Professional and modern designs", "Complete multi-page preview", "Direct editing in your browser", "Free PDF download"]),
        "/resume-format/": ("Resume Format Guide: Chronological, Functional, and Combination", "Compare chronological, functional, and combination resume formats and choose the structure that presents your experience clearly.", "Choose the right resume format for your story", "The layout should support the evidence. Reverse chronological is the clearest default, combination format can foreground relevant capabilities, and functional resumes require careful use because employers still expect a work history.", ["Chronological: best when recent experience is relevant", "Combination: useful for career changes and technical depth", "Functional: use sparingly and include clear dates", "Keep headings, spacing, and reading order consistent"]),
        "/cv-format/": ("CV Format Guide for International Applications", "Format a clear CV for international job applications with practical guidance on length, sections, typography, and regional expectations.", "A practical CV format for international roles", "Use the employer’s terminology and local convention. For most private-sector applications, a concise reverse-chronological CV with clear headings, relevant skills, and one or two readable pages is a strong default.", ["Check Letter vs A4 page size", "Follow local photo and personal-data norms", "Use reverse chronological experience", "Submit the requested PDF or DOCX format"]),
        "/resume-pdf/": ("Create a Resume PDF Online for Free", "Create, edit, and download a professional resume PDF online for free. Preview every page before exporting.", "Create a polished resume PDF online for free", "Build the complete resume in your browser, review the real page layout, and export a print-ready PDF without an account or payment.", ["Edit the complete template for free", "Review every included resume page", "Keep text selectable and links readable", "Download a print-ready PDF when finished"]),
    }
    for path, (title, desc, heading, intro, points) in core.items():
        crumb, crumb_schema = breadcrumb([("Home", "/"), (title, path)])
        list_html = "".join(f"<li>{esc(p)}</li>" for p in points)
        templates = TEMPLATES[:12] if "format" not in path else [t for t in TEMPLATES if "ats" in template_tags(t)][:12]
        body = f'''<div class="seo-shell">{crumb}<section class="seo-listing-hero"><span class="seo-kicker">Free online editing and download</span><h1>{esc(heading)}</h1><p class="seo-lede">{esc(intro)}</p><div class="seo-actions"><a class="button button--primary" href="/resume-templates/">Choose a template</a><a class="button button--outline" href="/career-advice/how-to-write-a-resume/">Read the writing guide</a></div></section><section class="seo-copy-grid"><div><h2>Build around readable, relevant evidence</h2><p>{esc(desc)} Start with the sections a recruiter expects, tailor the document to the actual role, and keep the final text selectable.</p><ul class="seo-checks">{list_html}</ul></div><aside class="seo-note"><strong>Completely free</strong><p>Edit, preview, and download your resume PDF without a card, account, or download credits.</p><a href="/resume-builder/">Open the free builder →</a></aside></section><section><div class="seo-section-heading"><span>Start with a design</span><h2>Recommended editable templates</h2></div><div class="seo-template-grid">{"".join(card(t) for t in templates)}</div></section></div>'''
        write_route(path, page(branded_title(title), desc, path, body, [{"@context": "https://schema.org", "@type": "WebPage", "name": title, "description": desc, "url": SITE + path}, crumb_schema]))


def generate_resume_builder():
    path = "/resume-builder/"
    title = "Free Resume Builder: Create a Resume Online"
    desc = "Use a free online resume builder with 105 editable templates. Create, edit, preview, and download every page as a PDF without paying."
    crumb, crumb_schema = breadcrumb([("Home", "/"), ("Free resume builder", path)])
    faq, faq_schema = faq_markup([
        ("Is the resume builder free?", "Yes. Choosing a template, editing the complete resume, previewing every page, and downloading the PDF are free."),
        ("Can I make a resume without creating an account?", "Yes. You can edit and download your resume without creating an account."),
        ("What does a PDF download cost?", "PDF downloads are free. There is no payment or download-credit limit."),
        ("Can I edit the actual template?", "Yes. The editor opens the selected template and all available pages. You can replace text directly and adjust supported elements."),
        ("Does ResumeNowOnline provide Word downloads?", "The current export product is PDF. We do not advertise DOCX or Google Docs downloads."),
    ])
    templates = [TEMPLATES[i] for i in (3, 7, 12, 20, 31, 42, 58, 72)]
    body = f'''<div class="seo-shell">{crumb}<section class="seo-tool-hero"><div><span class="seo-kicker">Free online resume maker</span><h1>Build your resume online for free</h1><p class="seo-lede">Choose from 105 professional resume templates, replace the sample content directly, preview the complete document, and download your PDF for free. No card or account is required.</p><div class="seo-actions"><a class="button button--primary" href="/resume-templates/">Create my resume</a><a class="button button--outline" href="#how-it-works">How it works</a></div><ul class="seo-checks"><li>Free resume creation, editing, and PDF download</li><li>One-page and multi-page templates</li><li>No account, card, or download credits</li></ul></div><div class="seo-tool-visual"><img src="/assets/template-previews/template-004.jpg" alt="Resume created with the free ResumeNowOnline builder" width="520" height="670"><div><strong>105</strong><span>editable templates</span></div></div></section><section class="seo-stat-row" aria-label="Resume builder highlights"><div><strong>Free</strong><span>from start to download</span></div><div><strong>105</strong><span>resume templates</span></div><div><strong>All pages</strong><span>included in preview</span></div><div><strong>PDF</strong><span>free to download</span></div></section><section class="seo-editorial" id="how-it-works"><h2>How to create a resume online</h2><div><h3>1. Choose a resume template</h3><p>Start with a layout that gives your most relevant experience enough room. Use a simple or ATS-friendly resume for application portals, a professional template for broad business roles, or a more expressive design when visual judgment is part of the job.</p><h3>2. Edit the complete resume</h3><p>Replace the sample text directly on the document. Add your contact information, summary, work experience, education, skills, and projects. Photo templates support image upload and positioning where a photo region is available.</p><h3>3. Review every page</h3><p>Check dates, contact details, links, line breaks, and page endings at normal zoom. Remove weak content before reducing font size or margins. The preview shows every page included with the original template.</p><h3>4. Download for free</h3><p>When the resume is final, select Download PDF and save it through the browser print dialog. No sign-in, payment, or download credits are required.</p></div></section><section><div class="seo-section-heading"><span>Popular starting points</span><h2>Professional resume templates</h2><p>Every design below opens as the actual template in the online resume editor.</p></div><div class="seo-template-grid">{"".join(card(t) for t in templates)}</div></section><section class="seo-copy-grid"><div><span class="seo-kicker">Write for the role</span><h2>A resume maker helps with layout. Your evidence earns attention.</h2><p>A strong resume names the target role, prioritizes recent relevant work, and explains what changed because of your contribution. Use numbers when they clarify scale, speed, quality, revenue, cost, or adoption.</p><p>Match relevant terminology from the job description naturally. Do not paste a keyword list or make claims you cannot support in an interview.</p><div class="seo-tag-list"><a href="/career-advice/how-to-write-a-resume/">How to write a resume</a><a href="/career-advice/resume-summary/">Resume summary</a><a href="/career-advice/resume-skills/">Skills for a resume</a><a href="/ats-resume-checker/">ATS resume checker</a></div></div><aside class="seo-note"><strong>Free from start to finish</strong><p>$0 to choose a template, edit every supported element, preview all pages, and save the finished PDF.</p><a href="/resume-templates/">Choose a free template →</a></aside></section>{faq}<section class="seo-final-cta"><span>Start free</span><h2>Create a professional resume now.</h2><p>Choose a template, edit it online, and download it for free.</p><a class="button button--light" href="/resume-templates/">Build my resume</a></section></div>'''
    app_schema = {"@context": "https://schema.org", "@type": "SoftwareApplication", "name": "ResumeNowOnline Free Resume Builder", "applicationCategory": "BusinessApplication", "operatingSystem": "Web", "url": SITE + path, "description": desc, "featureList": ["105 editable resume templates", "Direct text editing", "Multi-page resume preview", "Free PDF export"], "offers": {"@type": "Offer", "name": "Free resume builder and PDF download", "price": "0", "priceCurrency": "USD"}, "publisher": {"@id": SITE + "/#organization"}}
    write_route(path, page(branded_title(title), desc, path, body, [app_schema, crumb_schema, faq_schema]))


def generate_ats_checker():
    path = "/ats-resume-checker/"
    title = "Free ATS Resume Checker: Check Readability and Keywords"
    desc = "Use a free ATS resume checker to review headings, contact details, measurable results, length, and job-description keyword coverage in your browser."
    crumb, crumb_schema = breadcrumb([("Home", "/"), ("ATS resume checker", path)])
    faq, faq_schema = faq_markup([
        ("What does this ATS resume checker test?", "It checks practical readability signals including standard section headings, contact details, length, bullets, action verbs, measurable results, and optional job-description keyword coverage."),
        ("Does a high score guarantee an interview?", "No. Employers use different systems and hiring criteria. The result is a writing and readability review, not a prediction or certification."),
        ("Is my resume uploaded?", "No. This checker runs in your browser. The pasted text is not sent to ResumeNowOnline by this page."),
        ("Can I check a PDF?", "Copy selectable text from the PDF and paste it into the checker. If the text copies in the wrong order, choose a simpler layout or fix the source file."),
    ])
    body = f'''<div class="seo-shell">{crumb}<section class="seo-listing-hero"><span class="seo-kicker">Free browser-based review</span><h1>ATS resume checker</h1><p class="seo-lede">Paste your resume text to check common readability signals. Add a job description to compare important terms. Your text stays in this browser.</p></section><section class="seo-checker" aria-labelledby="checker-title"><div class="seo-checker-form"><div class="seo-section-heading"><span>Resume check</span><h2 id="checker-title">Review your resume text</h2></div><label for="atsResumeText">Resume text <small>Required</small></label><textarea id="atsResumeText" rows="16" placeholder="Paste the selectable text from your resume here..."></textarea><label for="atsJobText">Job description <small>Optional, improves keyword comparison</small></label><textarea id="atsJobText" rows="9" placeholder="Paste the target job description here..."></textarea><button class="button button--primary" id="atsAnalyze" type="button">Check my resume</button><p class="seo-privacy-note">Analysis runs locally in your browser. This tool does not upload the pasted text.</p></div><aside class="seo-checker-results" id="atsResults" aria-live="polite"><div class="seo-score"><span>Your review</span><strong id="atsScore">—</strong><small id="atsLabel">Paste your resume to begin</small></div><div id="atsChecks" class="seo-check-list"></div><div id="atsKeywords" class="seo-keyword-result" hidden><strong>Job-description terms found</strong><p id="atsKeywordCopy"></p></div></aside></section><section class="seo-copy-grid"><div><span class="seo-kicker">What the score means</span><h2>Use the checker as a review, not a promise</h2><p>Applicant tracking systems differ by employer. Some parse files, some support recruiter search, and some connect applications with screening workflows. No public checker can guarantee how every system or recruiter will evaluate a resume.</p><p>This tool focuses on signals you can control: clear headings, selectable text, complete contact information, readable length, evidence-led bullets, and relevant terminology used honestly.</p><div class="seo-tag-list"><a href="/career-advice/ats-friendly-resume/">ATS-friendly resume guide</a><a href="/resume-templates/ats/">ATS-friendly templates</a><a href="/career-advice/resume-bullet-points/">Stronger bullet points</a></div></div><aside class="seo-note"><strong>Before uploading a file</strong><p>Open the final PDF, select all text, and paste it into a plain-text editor. The name, headings, dates, and bullets should appear in a sensible order.</p><a href="/resume-format/">Compare resume formats →</a></aside></section>{faq}<section class="seo-final-cta"><span>Improve the layout</span><h2>Start with an ATS-friendly resume template.</h2><p>Edit the complete document online for free.</p><a class="button button--light" href="/resume-templates/ats/">Browse ATS templates</a></section></div>'''
    script = r'''<script>(()=>{const resume=document.getElementById("atsResumeText"),job=document.getElementById("atsJobText"),button=document.getElementById("atsAnalyze"),scoreEl=document.getElementById("atsScore"),labelEl=document.getElementById("atsLabel"),checksEl=document.getElementById("atsChecks"),keywordsBox=document.getElementById("atsKeywords"),keywordsCopy=document.getElementById("atsKeywordCopy");const stop=new Set("a an and are as at be by for from has have in is it its of on or that the this to with will you your our we they their role work working experience years skills required preferred including using use who what when where how can should".split(" "));function words(value){return(value.toLowerCase().match(/[a-z][a-z0-9+#.-]{2,}/g)||[])}function add(label,pass,note,weight,state){const row=document.createElement("div");row.className=pass?"pass":"improve";const mark=document.createElement("i");mark.textContent=pass?"✓":"!";const copy=document.createElement("span");const strong=document.createElement("strong");strong.textContent=label;const small=document.createElement("small");small.textContent=note;copy.append(strong,small);row.append(mark,copy);checksEl.append(row);if(pass)state.value+=weight}button.addEventListener("click",()=>{const text=resume.value.trim(),target=job.value.trim();if(!text){resume.focus();labelEl.textContent="Paste your resume text first";return}checksEl.replaceChildren();const state={value:0},count=words(text).length,lower=text.toLowerCase(),lines=text.split(/\n+/).map(v=>v.trim()).filter(Boolean);add("Readable resume length",count>=180&&count<=1100,`${count} words; most concise resumes fall between about 180 and 1,100 words.`,12,state);add("Email address",/[\w.+-]+@[\w.-]+\.[a-z]{2,}/i.test(text),"Include a professional email address in the contact section.",8,state);add("Phone number",/(?:\+?\d[\d ().-]{7,}\d)/.test(text),"Include a reachable phone number when appropriate for the market.",6,state);for(const [name,pattern,weight] of [["Experience heading",/\b(work experience|professional experience|experience|employment)\b/i,12],["Education heading",/\b(education|academic background)\b/i,8],["Skills heading",/\b(skills|technical skills|core competencies)\b/i,8]])add(name,pattern.test(text),"Use a clear, conventional section heading.",weight,state);const bulletLines=lines.filter(line=>/^[•●▪◦*-]\s+/.test(line)).length;add("Scannable bullet points",bulletLines>=3,`${bulletLines} bullet-style lines found; use concise bullets for recent achievements.`,10,state);const actionMatches=lower.match(/\b(achieved|analyzed|built|created|delivered|designed|developed|drove|improved|increased|launched|led|managed|optimized|reduced|resolved|saved|streamlined)\b/g)||[];add("Action-led evidence",actionMatches.length>=3,`${actionMatches.length} strong action verbs found.`,10,state);const metrics=(text.match(/(?:\b\d+(?:\.\d+)?%|\$\s?\d|\b\d+[kKmMbB]\b|\b\d{2,}\b)/g)||[]).length;add("Measurable results",metrics>=2,`${metrics} numeric proof points found; use numbers only when they add truthful context.`,10,state);add("Plain-text headings",!/[★☆◆◇▶►]/.test(text),"Avoid decorative symbols in essential headings and contact details.",6,state);if(target){const resumeSet=new Set(words(text));const counts=new Map();for(const term of words(target)){if(stop.has(term)||term.length<4)continue;counts.set(term,(counts.get(term)||0)+1)}const important=[...counts].sort((a,b)=>b[1]-a[1]).slice(0,18).map(x=>x[0]);const found=important.filter(term=>resumeSet.has(term));const coverage=important.length?found.length/important.length:0;add("Job-description keyword coverage",coverage>=.45,`${found.length} of ${important.length} recurring job terms found. Use only terms that accurately describe your experience.`,10,state);keywordsBox.hidden=false;keywordsCopy.textContent=found.length?found.join(", "):"No recurring job-description terms were found in the resume yet."}else{keywordsBox.hidden=true;state.value=Math.round(state.value/90*100)}const final=Math.min(100,Math.round(state.value));scoreEl.textContent=String(final);labelEl.textContent=final>=80?"Strong foundation":final>=60?"Good start; review the flagged items":"Several readability basics need attention";document.getElementById("atsResults").scrollIntoView({behavior:"smooth",block:"center"})})})();</script>'''
    app_schema = {"@context": "https://schema.org", "@type": "SoftwareApplication", "name": "ResumeNowOnline ATS Resume Checker", "applicationCategory": "BusinessApplication", "operatingSystem": "Web", "url": SITE + path, "description": desc, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}, "publisher": {"@id": SITE + "/#organization"}}
    write_route(path, page(branded_title(title), desc, path, body, [app_schema, crumb_schema, faq_schema], extra_body=script))


def generate_support_files():
    routes = ["/", "/resume-builder/", "/resume-templates/", "/resume-examples/", "/ats-resume-checker/", "/career-advice/", "/career-advice/resume-guides-by-profession/", "/cv-maker/", "/cv-templates/", "/resume-format/", "/cv-format/", "/resume-pdf/", "/pricing.html", "/product.html", "/contact.html", "/privacy.html", "/terms.html", "/refunds.html"]
    routes += [f'/resume-templates/{t["slug"]}/' for t in TEMPLATES]
    routes += [f"/resume-templates/{slug}/" for slug in CATEGORIES if any(slug in template_tags(t) for t in TEMPLATES)]
    routes += [f"/career-advice/{slug}/" for slug in GUIDES]
    routes += [f"/resume-examples/{slug}/" for slug in ROLE_GUIDES]
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
    generate_profession_hub()
    generate_jobs()
    generate_core_pages()
    generate_resume_builder()
    generate_ats_checker()
    generate_support_files()


if __name__ == "__main__":
    main()
