"""Runtime shared helpers."""

from __future__ import annotations

import logging

_NOISY_LOGGERS = [
    "webull.core.client",
    "webull.core.http.initializer.client_initializer",
    "webull.core.http.initializer.token.token_storage",
    "webull.core.http.initializer.token.token_operation",
]


def set_sdk_logging(verbose: bool) -> None:
    """Control SDK log level. Suppress noisy logs by default."""
    if verbose:
        return
    for name in _NOISY_LOGGERS:
        logging.getLogger(name).setLevel(logging.CRITICAL)
