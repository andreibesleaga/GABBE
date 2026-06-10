# SPDX-License-Identifier: Apache-2.0
"""Content-addressed disk cache for repeated deterministic operations.

A cost-optimization primitive: when the same input is processed again, return
the stored result instead of recomputing (and, for LLM calls, instead of paying
for the same tokens again). Keys are sha256 of the canonicalized input, so the
cache is safe to share and never returns a stale result for changed input.

Opt-in by design — callers decide when memoization is correct (it is correct for
deterministic, side-effect-free operations such as temperature-0 LLM calls,
skill compilation, or research lookups; it is NOT correct for time-sensitive or
randomized operations).
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path

logger = logging.getLogger("gabbe.cache")


def content_key(*parts) -> str:
    """Stable sha256 over the canonical JSON of the given parts."""
    payload = json.dumps(parts, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class ContentCache:
    """A tiny JSON-file content cache rooted at a directory.

    Best-effort: any I/O error degrades to a miss / no-op rather than raising,
    so enabling the cache can never break a run.
    """

    def __init__(self, root: Path, namespace: str = "default"):
        self.dir: Path | None = Path(root) / namespace
        try:
            self.dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:  # pragma: no cover - unusual fs failure
            logger.warning("cache dir unavailable (%s); caching disabled", e)
            self.dir = None

    def _path(self, key: str) -> Path:
        assert self.dir is not None  # callers guard on self.dir before calling
        return self.dir / f"{key}.json"

    def get(self, key: str):
        """Return the cached value for *key*, or None on miss / error."""
        if self.dir is None:
            return None
        p = self._path(key)
        if not p.exists():
            return None
        try:
            return json.loads(p.read_text(encoding="utf-8"))["value"]
        except (OSError, ValueError, KeyError):
            return None

    def set(self, key: str, value) -> None:
        """Store *value* under *key* (best-effort; errors are swallowed)."""
        if self.dir is None:
            return
        try:
            self._path(key).write_text(
                json.dumps({"value": value}, ensure_ascii=False), encoding="utf-8"
            )
        except (OSError, TypeError) as e:  # pragma: no cover - serialization/fs failure
            logger.debug("cache write skipped for %s: %s", key[:12], e)
