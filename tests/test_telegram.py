"""Tests for the Telegram Notifier module."""
import pytest
from src.telegram_notifier import TelegramNotifier
from src.feed_fetcher import Article


class TestTelegramNotifier:
    """Test that TelegramNotifier formats teaser messages."""

    def _sample_articles(self):
        return [
            Article(
                title="AI Article 1",
                summary="Summary of AI article.",
                url="https://example.com/ai1",
                source="Source A",
                date="Wed, 13 May 2026 00:00:00 GMT",
                category="ai",
                golden_nugget="This is the AI golden nugget.",
            ),
            Article(
                title="Design Article 1",
                summary="Summary of design article.",
                url="https://example.com/design1",
                source="Source B",
                date="Wed, 13 May 2026 00:00:00 GMT",
                category="design",
                golden_nugget="This is the design golden nugget.",
            ),
            Article(
                title="Product Article 1",
                summary="Summary of product article.",
                url="https://example.com/product1",
                source="Source C",
                date="Wed, 13 May 2026 00:00:00 GMT",
                category="product",
                golden_nugget="This is the product golden nugget.",
            ),
        ]

    def test_teaser_contains_golden_nuggets(self):
        """Teaser message includes golden nuggets."""
        notifier = TelegramNotifier()
        message = notifier.format_teaser(self._sample_articles(), "https://example.com/digest")
        assert "AI golden nugget" in message
        assert "design golden nugget" in message
        assert "product golden nugget" in message

    def test_teaser_includes_digest_link(self):
        """Teaser includes link to full digest."""
        notifier = TelegramNotifier()
        message = notifier.format_teaser(self._sample_articles(), "https://example.com/digest")
        assert "https://example.com/digest" in message

    def test_teaser_no_emojis(self):
        """Teaser contains no emojis."""
        notifier = TelegramNotifier()
        message = notifier.format_teaser(self._sample_articles(), "https://example.com/digest")
        # Check no emoji characters
        for char in message:
            assert ord(char) < 0x1F600 or ord(char) > 0x1F64F, f"Emoji found: {char}"

    def test_teaser_limited_to_top_nuggets(self):
        """Teaser shows at most 5 golden nuggets."""
        articles = self._sample_articles() * 3  # 9 articles
        notifier = TelegramNotifier()
        message = notifier.format_teaser(articles, "https://example.com/digest", max_nuggets=3)
        # Count golden nugget occurrences
        count = message.count("golden nugget")
        assert count <= 3
