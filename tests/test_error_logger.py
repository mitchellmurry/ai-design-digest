"""Tests for the Error Logger module."""
import pytest
import os
import tempfile
from src.error_logger import ErrorLogger


class TestErrorLogger:
    """Test that ErrorLogger writes errors to log file."""

    def test_log_error_writes_to_file(self):
        """Logging an error appends to the log file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = os.path.join(tmpdir, "errors.log")
            logger = ErrorLogger(log_path)
            logger.log("TLDR AI", "TimeoutError", "Connection timed out")
            content = open(log_path).read()
            assert "TLDR AI" in content
            assert "TimeoutError" in content
            assert "Connection timed out" in content

    def test_log_includes_timestamp(self):
        """Logged error includes timestamp."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = os.path.join(tmpdir, "errors.log")
            logger = ErrorLogger(log_path)
            logger.log("Source", "Error", "message")
            content = open(log_path).read()
            assert "2026" in content  # timestamp contains year

    def test_multiple_errors_append(self):
        """Multiple errors are appended, not overwritten."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = os.path.join(tmpdir, "errors.log")
            logger = ErrorLogger(log_path)
            logger.log("Source A", "Error 1", "msg1")
            logger.log("Source B", "Error 2", "msg2")
            content = open(log_path).read()
            assert "Source A" in content
            assert "Source B" in content
            assert content.count("\n") >= 2

    def test_empty_log_returns_empty(self):
        """Reading empty log returns empty list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = os.path.join(tmpdir, "errors.log")
            logger = ErrorLogger(log_path)
            errors = logger.read()
            assert errors == []

    def test_creates_log_file_if_missing(self):
        """Logger creates log file if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = os.path.join(tmpdir, "errors.log")
            assert not os.path.exists(log_path)
            logger = ErrorLogger(log_path)
            logger.log("Source", "Error", "msg")
            assert os.path.exists(log_path)
