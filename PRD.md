# PRD: AI + Design Daily Digest

## Problem Statement

Mitch needs a single place to stay current on AI, design, and product development news without doomscrolling multiple sites. Current workflow involves manually visiting TLDR AI, Hacker News, every.to, Lenny's Newsletter, and tracking Hermes Agent community updates. This is time-consuming, inconsistent, and misses content. He wants a curated daily digest that surfaces only the most valuable content, summarized with actionable golden nuggets, delivered to his phone each morning before he starts his day.

## Solution

A cron-driven pipeline that fetches content from RSS feeds and a personal queue, pre-filters for relevance and freshness, uses an LLM to rank and summarize, generates a static HTML digest page, and sends a teaser notification to Telegram. Hosted on GitHub Pages with date-based archives. Self-curation via Telegram `/save` command allows manual article inclusion.

## User Stories

1. As Mitch, I want to receive a Telegram notification at 5:00 AM CT each morning with the top golden nuggets from today's digest, so that I can scan highlights before getting out of bed.
2. As Mitch, I want to click through from the Telegram notification to a full HTML digest page, so that I can read deeper on items that interest me.
3. As Mitch, I want the digest page to be mobile-friendly and readable on my phone, so that I can read during my morning routine.
4. As Mitch, I want the digest page to be accessible via a public URL without search engine indexing, so that I can share links with friends without the content appearing in Google.
5. As Mitch, I want past digests to be archived by date and browsable, so that I can reference something I read last week.
6. As Mitch, I want the digest to cover AI news, design insights, and product development content, so that I stay current across all three domains.
7. As Mitch, I want content from TLDR AI included in the digest, so that I don't miss curated AI news.
8. As Mitch, I want Hacker News filtered for AI, design, and product topics included, so that I get relevant HN content without the noise.
9. As Mitch, I want content from every.to included, so that I get high-quality essays and analysis.
10. As Mitch, I want Lenny's Newsletter written content included (not podcast audio), so that I get product development insights.
11. As Mitch, I want Hermes Agent GitHub Releases included, so that I can track what the community is building.
12. As Mitch, I want to send a `/save <url>` command to Telegram to queue articles for the next digest, so that I can flag interesting content I find during the day.
13. As Mitch, I want the `/save` command to confirm receipt with a brief acknowledgment, so that I know the URL was captured.
14. As Mitch, I want saved URLs to be stored in a `queue.md` file, so that they persist across runs and can be inspected manually.
15. As Mitch, I want articles older than 24 hours to be automatically filtered out, so that the digest only contains fresh content.
16. As Mitch, I want duplicate articles across sources to be detected and merged, so that I don't see the same story twice.
17. As Mitch, I want the LLM to first rank articles by title alone (cheap pass), then only fully summarize the top items, so that token costs stay low.
18. As Mitch, I want the top 10-15 items to receive full summaries with key takeaways, so that I get depth on what matters most.
19. As Mitch, I want each summary to include a "golden nugget" — a single actionable sentence — highlighted at the top of the digest, so that I can quickly extract the most valuable insight.
20. As Mitch, I want the golden nuggets section to appear at the very top of the digest page, so that it's the first thing I see.
21. As Mitch, I want the digest page grouped by category (AI, Design, Product, Community), so that I can focus on the area I care about most.
22. As Mitch, I want the digest HTML to be generated from a Jinja2 template, so that the visual style is consistent and easy to update.
23. As Mitch, I want the digest to use a clean, magazine-style layout with mobile-first responsive design, so that it's pleasant to read on any device.
24. As Mitch, I want the digest to contain no emojis in any content or UI, so that it matches his preferred communication style.
25. As Mitch, I want failed sources to be silently skipped without disrupting the rest of the digest, so that one broken feed doesn't ruin the whole output.
26. As Mitch, I want source errors to be logged to an internal file, so that he can ask about failures later and diagnose issues.
27. As Mitch, I want the Telegram teaser to show 3-5 golden nuggets with a link to the full digest, so that the notification is scannable and not overwhelming.
28. As Mitch, I want the digest pipeline to run as a Hermes cron job, so that it uses infrastructure he already has without additional hosting costs.
29. As Mitch, I want the LLM curation interface to be pluggable, so that he can transition from Hermes to a dedicated API (OpenAI, Anthropic) later without rewriting the pipeline.
30. As Mitch, I want the cron job to run at 5:00 AM US Central time, so that the digest is ready when he wakes up.
31. As Mitch, I want the GitHub Pages site to live at a clean URL structure (`/digest/YYYY-MM-DD.html`), so that archive links are intuitive.
32. As Mitch, I want a homepage (`/digest/index.html`) showing the latest digest with links to past ones, so that he has a single entry point.
33. As Mitch, I want the `queue.md` file to be part of the git repo, so that the personal queue is versioned and backed up.
34. As Mitch, I want the pipeline to handle sources returning unexpected formats gracefully, so that parse errors don't crash the run.
35. As Mitch, I want the digest to include source attribution (publication name + link) for each item, so that he can click through to the original.

## Implementation Decisions

### Modules

1. **Feed Fetcher** — Parses RSS feeds using `feedparser`. Each source has a config entry (name, URL, category, type). Returns normalized article objects (title, summary, URL, source, published date, category). Also reads `queue.md` for manually queued URLs and fetches HN stories via the Algolia API filtered by keywords.

2. **Pre-Filter** — Pure Python, zero LLM cost. Filters articles by: age (24h window), deduplication (URL + title similarity), topic relevance (keyword matching against category). Input: raw articles from Feed Fetcher. Output: filtered article list.

3. **Curation Pipeline** — Orchestrator that chains: Fetch → Pre-Filter → Title-Only Ranking → Full Summarization → Output. Runs as a Hermes cron job. Configurable token budget. Handles partial failures (skip failed sources, continue with available content).

4. **LLM Interface** — Abstract class with a `summarize` method. Initial implementation wraps Hermes cron context. Future implementations can wrap OpenAI, Anthropic, or local models. Contract: receives article list, returns ranked summaries with golden nuggets.

5. **HTML Generator** — Jinja2 template that takes curated content and renders a static HTML page. Outputs to `digest/YYYY-MM-DD.html` and updates `digest/index.html`. Template includes: golden nuggets section, category sections, source links, date header, archive navigation.

6. **Telegram Notifier** — Sends a formatted teaser message to Mitch's personal Telegram DM via Hermes send_message. Message contains top 3-5 golden nuggets as bullet points + link to full digest page.

7. **Self-Curation** — Listens for `/save <url>` commands in Telegram. Appends URL + timestamp to `queue.md`. Returns confirmation message. The Feed Fetcher reads `queue.md` each run and fetches those URLs.

8. **Error Logger** — Writes errors to `digest/logs/errors.log` with timestamp, source name, error type, and message. Silent during normal operation. Queryable by asking about source errors.

### Interfaces

- Feed Fetcher → Pre-Filter: `List[Article]` → `List[Article]`
- Pre-Filter → Curation Pipeline: `List[Article]` → `List[Article]`
- Curation Pipeline → LLM Interface: `List[Article]` → `List[CuratedItem]`
- LLM Interface → HTML Generator: `List[CuratedItem]` → HTML file
- Curation Pipeline → Telegram Notifier: `List[CuratedItem]` → Telegram message

### Architecture Decisions

- Static HTML over dynamic server — zero maintenance, GitHub Pages handles hosting
- Hermes cron over system cron — leverages existing infrastructure, agent handles LLM calls natively
- Pluggable LLM interface — start with Hermes, transition to dedicated API when token budget or quality demands it
- `queue.md` as git-tracked file — simple, inspectable, versioned
- Silent error skipping — resilience over reporting (user can query logs on demand)

## Testing Decisions

- **What makes a good test:** Test external behavior (input → output), not implementation details. Mock external services (RSS feeds, Telegram API, LLM). Test edge cases: empty feeds, malformed RSS, duplicate articles, missing fields.
- **Modules to test:**
  - Feed Fetcher — mock RSS responses, verify normalization
  - Pre-Filter — unit tests with known article sets, verify filtering logic
  - HTML Generator — snapshot tests against golden HTML files
  - Telegram Notifier — mock API, verify message format
- **Prior art:** Standard Python testing with pytest. No existing tests in this project (greenfield).

## Out of Scope

- Podcast transcription and inclusion (deferred to future phase)
- X/Twitter API search (cost-prohibitive at $100/month)
- User authentication on the digest site (public access, robots.txt only)
- Multiple user support (personal tool for Mitch only)
- Real-time updates (runs once daily at 5:00 AM CT)
- Paid API costs for LLM curation (start with Hermes, transition later if needed)
- Email delivery (Telegram only for now)
- Analytics or read tracking

## Further Notes

- The repo is currently private on GitHub. It will need to be made public before GitHub Pages deployment.
- `robots.txt` with `Disallow: /` and `<meta name="robots" content="noindex">` will prevent search engine indexing while keeping direct URL access public.
- The `/save` Telegram command needs to be implemented as a Hermes skill or webhook handler.
- Source RSS URLs need to be validated before building the Feed Fetcher — some sources (every.to, Lenny's) may have non-standard feed formats.
- Token budget should be configurable. Start lean (~$0.05-0.10/day estimate) and scale up only if quality demands it.
