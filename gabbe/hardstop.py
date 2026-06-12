# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import time

from .config import (
    GABBE_MAX_ITERATIONS,
    GABBE_MAX_RECURSION_DEPTH,
)


class HardStopTriggered(Exception):
    pass


class MaxIterationsExceeded(HardStopTriggered):
    pass


class MaxDepthExceeded(HardStopTriggered):
    pass


class TimeoutExceeded(HardStopTriggered):
    pass


class HardStop:
    def __init__(
        self,
        max_iterations: int | None = None,
        max_depth: int | None = None,
        timeout_sec: int | float | None = None,
    ) -> None:
        from .config import GABBE_MAX_WALL_TIME

        self.max_iterations = max_iterations if max_iterations is not None else GABBE_MAX_ITERATIONS
        self.max_depth = max_depth if max_depth is not None else GABBE_MAX_RECURSION_DEPTH
        self.timeout_sec = timeout_sec if timeout_sec is not None else GABBE_MAX_WALL_TIME

        self.iterations = 0
        self._start_time = time.monotonic()

    def tick(self, depth: int = 0) -> None:
        self.iterations += 1

        if self.iterations > self.max_iterations:
            raise MaxIterationsExceeded(
                f"Hard stop: Iteration limit ({self.max_iterations}) exceeded."
            )

        if depth > self.max_depth:
            raise MaxDepthExceeded(f"Hard stop: Recursion depth ({self.max_depth}) exceeded.")

        if time.monotonic() - self._start_time > self.timeout_sec:
            raise TimeoutExceeded(f"Hard stop: Timeout ({self.timeout_sec}s) exceeded.")

    def remaining_steps(self) -> int:
        return max(0, self.max_iterations - self.iterations)

    def should_wrap_up(self, threshold: int = 2) -> bool:
        return self.remaining_steps() <= threshold
