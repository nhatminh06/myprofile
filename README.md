# Minh Pham — Personal Portfolio

Personal engineering portfolio for Minh Pham.

Live: [https://minhpham06.com](https://minhpham06.com)

## About the portfolio

A static, multi-page site covering:

- **Experience** — professional experience timeline (VietinBank, FPT Software), on the About page
- **Projects** — real repositories: distributed systems, data engineering, ML infrastructure, Linux systems, and DevSecOps work
- **Technical writing** — a blog documenting what was built, what broke, and what was learned, sourced from the actual project repositories
- **Resume / contact** — resume download and contact links (email, GitHub, LinkedIn)

## Current focus

- Distributed systems
- Platform engineering
- Backend engineering
- Data engineering
- ML systems
- Linux and systems programming

## Tech

```text
HTML
CSS
Vanilla JavaScript
```

No frontend framework, no backend, no database, no build step. The site is a directory of static files.

## Local development

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000`.

## Structure

```text
.
├── index.html          # Home
├── about.html          # About + experience timeline
├── projects.html       # Project cards
├── blog.html           # Blog index / filters
├── contact.html        # Contact
├── 404.html            # Custom 404 page
├── robots.txt
├── sitemap.xml
├── blog/                # Individual blog post pages
│   └── *.html
└── static/
    ├── style.css
    ├── script.js
    ├── favicon.png
    ├── avatar.jpg / cano.jpeg / lake.jpeg / scene.jpeg
    └── Nhat Minh_Resume.pdf
```

## Content updates

**Adding a project card** — edit `projects.html`, following the existing `.project-card` markup (name, status, description, `.project-tech-tags`, and a GitHub link). Keep the featured/secondary split: strongest, most current projects go in the main `.projects-grid`; smaller or older work goes under "Additional Work" in `.projects-grid--secondary`.

**Adding a blog post** — copy an existing file under `blog/` as a template (keep the shared header/nav/footer), write the post, then add a matching `<article class="blog-card">` entry to `blog.html` with accurate `data-tags` for the filter buttons. Posts are auto-sorted newest-first by `static/script.js` based on the `.blog-date` text, so use a real, parseable date.

**Replacing the résumé** — drop the new PDF into `static/`. If the filename changes, update every `href="/static/...resume...pdf"` reference across the site (currently in each page's footer and the homepage hero).

**Updating profile links** — GitHub, LinkedIn, and email addresses are inlined in each page's footer and, where relevant, on the Contact page. Update all instances together to avoid stale links.

## Deployment

The site is deployed as static files. Pushing to `main` deploys the update; there is no separate build step. The custom domain is fronted by Cloudflare.
