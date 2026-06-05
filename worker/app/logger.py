from __future__ import annotations

import logging
import sys


def setup_logger(debug: bool = False) -> logging.Logger:
    logger = logging.getLogger("gt7-worker")
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG if debug else logging.INFO)
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))

    logger.addHandler(handler)
    return logger
