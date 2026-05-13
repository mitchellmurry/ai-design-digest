"""Deployment Manager — handles GitHub Pages output structure."""
from pathlib import Path


class DeploymentManager:
    """Manages deployment artifacts: robots.txt, homepage, output paths."""

    def get_robots_txt(self) -> str:
        """Return robots.txt content that blocks all crawlers."""
        return "User-agent: *\nDisallow: /\n"

    def get_digest_path(self, date: str) -> str:
        """Return the output path for a digest (e.g., digest/2026-05-13.html)."""
        return f"digest/{date}.html"

    def get_homepage_path(self) -> str:
        """Return the output path for the homepage."""
        return "digest/index.html"

    def generate_homepage(self, latest_date: str, archive_dates: list = None) -> str:
        """Generate homepage HTML with latest digest and archive links."""
        archive_links = ""
        if archive_dates:
            for date in sorted(archive_dates, reverse=True):
                archive_links += f'            <li><a href="{date}.html">{date}</a></li>\n'

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="noindex, nofollow">
    <title>AI + Design Daily Digest</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #1a1a1a;
            background: #fafafa;
            padding: 2rem;
            max-width: 600px;
            margin: 0 auto;
        }}
        h1 {{ font-size: 1.5rem; margin-bottom: 1rem; }}
        .latest {{ margin-bottom: 2rem; }}
        .latest a {{
            display: inline-block;
            padding: 0.75rem 1.5rem;
            background: #1a1a1a;
            color: #fff;
            text-decoration: none;
            border-radius: 4px;
        }}
        .latest a:hover {{ background: #333; }}
        h2 {{ font-size: 1rem; color: #666; margin-bottom: 0.5rem; }}
        ul {{ list-style: none; }}
        li {{ padding: 0.25rem 0; }}
        li a {{ color: #1a1a1a; text-decoration: none; }}
        li a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <h1>AI + Design Daily Digest</h1>

    <section class="latest">
        <a href="{latest_date}.html">Read Today's Digest ({latest_date})</a>
    </section>

    {"<h2>Past Digests</h2>" + chr(10) + "<ul>" + chr(10) + archive_links + "</ul>" if archive_links else ""}
</body>
</html>"""

    def save_file(self, content: str, path: str) -> None:
        """Write content to file, creating directories as needed."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(content, encoding="utf-8")
