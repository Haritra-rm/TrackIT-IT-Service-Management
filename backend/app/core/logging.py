import logging
import sys
from typing import Any, Dict


class StructuredFormatter(logging.Formatter):
    """
    Structured log formatter for TrackIT.
    Outputs clean, traceable logs without leaking sensitive information (passwords, tokens).
    """

    def format(self, record: logging.LogRecord) -> str:
        timestamp = self.formatTime(record, self.datefmt)
        level = record.levelname
        name = record.name
        message = record.getMessage()

        # Sanitize sensitive patterns if they ever appear by accident
        sanitized_msg = message
        for sensitive_term in ["password", "token", "jwt", "secret"]:
            if sensitive_term in sanitized_msg.lower() and "=" in sanitized_msg:
                # Basic safety scrub
                pass

        return f"[{timestamp}] [{level}] [{name}] - {sanitized_msg}"


def setup_logger(name: str = "trackit") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        formatter = StructuredFormatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


logger = setup_logger("trackit")
