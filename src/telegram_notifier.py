"""Telegram Notifier — formats teaser messages for Telegram DM."""
from typing import List
from src.feed_fetcher import Article


class TelegramNotifier:
    """Formats digest teaser messages for Telegram."""

    def format_teaser(self, articles: List[Article], digest_url: str, max_nuggets: int = 5) -> str:
        """Format a teaser message with top golden nuggets and digest link."""
        # Collect articles with golden nuggets
        nugget_articles = [a for a in articles if a.golden_nugget]

        # Limit to top N
        nugget_articles = nugget_articles[:max_nuggets]

        # Build message
        lines = ["AI + Design Daily Digest", ""]

        for article in nugget_articles:
            lines.append(f"- {article.golden_nugget}")

        lines.append("")
        lines.append(f"Read more: {digest_url}")

        return "\n".join(lines)
