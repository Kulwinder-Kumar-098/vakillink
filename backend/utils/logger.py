"""
utils/logger.py
Structured, colourised logging for the Vakilink RAG pipeline.
"""
import logging
import sys
from typing import Optional


# ANSI colour codes
_RESET  = "\033[0m"
_BOLD   = "\033[1m"
_GREEN  = "\033[92m"
_YELLOW = "\033[93m"
_RED    = "\033[91m"
_CYAN   = "\033[96m"
_GREY   = "\033[90m"


LEVEL_COLORS = {
    logging.DEBUG:    _GREY,
    logging.INFO:     _GREEN,
    logging.WARNING:  _YELLOW,
    logging.ERROR:    _RED,
    logging.CRITICAL: _RED + _BOLD,
}


class _ColorFormatter(logging.Formatter):
    """Adds ANSI colours and a fixed-width module prefix to each log line."""

    FMT = "{color}[{level}]{reset} {bold}{name}{reset} » {msg}"

    def format(self, record: logging.LogRecord) -> str:
        color = LEVEL_COLORS.get(record.levelno, _RESET)
        level = record.levelname[:4]
        name  = record.name.split(".")[-1]          # last segment only
        msg   = record.getMessage()

        if record.exc_info:
            msg += "\n" + self.formatException(record.exc_info)

        return self.FMT.format(
            color=color, level=level, reset=_RESET,
            bold=_BOLD,  name=name,  msg=msg,
        )


def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Return a named logger configured with the colour formatter.
    Idempotent — calling twice returns the same logger.
    """
    logger = logging.getLogger(name)

    if logger.handlers:          # already configured
        return logger

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_ColorFormatter())
    logger.addHandler(handler)
    logger.setLevel(level or logging.INFO)
    logger.propagate = False     # prevent duplicate root-logger output

    return logger
