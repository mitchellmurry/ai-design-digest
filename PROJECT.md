# AI + Design Daily Digest

A personal daily digest that curates key news, findings, and learnings around AI, Design, and Product Development — summarized by AI with golden nuggets and key takeaways.

## Topics

- **AI** — news, tools, research, industry shifts
- **Design** — product design, UI/UX, designers using AI, visual trends
- **Product Development** — strategy, launches, frameworks, lessons learned

## Sources

### RSS Feeds
- **AI**: TLDR AI, ImportAI, HuggingFace blog, The Verge AI
- **Design**: Smashing Magazine, Nielsen Norman Group, UX Collective, Sidebar.io
- **Product**: Product Hunt, Lenny's Newsletter, Stratechery

### Podcasts
- The AI Podcast (NVIDIA)
- Design Better
- UI Breakfast
- Lenny's Podcast

### Websites
- Hacker News (filtered for AI + design topics)
- Curated recommendation sources

### X / Twitter
- Curated accounts (TBD — to be added)

## Curation Style

- **AI-summarized digests** with key takeaways for each item
- **Golden nuggets** — the most valuable insights extracted and highlighted
- LLM does the heavy lifting to filter noise and surface the best content

## Access

- **Web page** — responsive, mobile-friendly, works on phone and computer
- **Telegram push** — morning notification with highlights + link to full digest
- **Archives** — past digests browsable by date

## Visual Style

- Magazine-style daily digest
- Grouped by category (AI / Design / Product)
- Clean, readable, designed for daily consumption
- Mobile-first responsive layout

## Technical Plan

1. **Fetch layer** — Python script pulls from RSS feeds, podcast RSS, websites, X
2. **Curation layer** — LLM summarizes each item, extracts takeaways, picks golden nuggets
3. **Generation layer** — Static HTML page generated with Jinja2 (responsive, archived)
4. **Delivery layer** — Telegram message with highlights + link
5. **Scheduling** — Cron job runs every morning

## Tech Stack

- Python 3
- feedparser (RSS parsing)
- Jinja2 (HTML templating)
- requests (HTTP)
- LLM API for summarization
- Simple HTTP server or GitHub Pages for hosting

## Status

- [x] Project direction defined
- [ ] Source URLs gathered and validated
- [ ] Fetch layer built
- [ ] Curation / summarization pipeline
- [ ] HTML template and page generation
- [ ] Telegram delivery
- [ ] Cron job setup
- [ ] First run and review
