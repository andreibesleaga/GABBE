# SPDX-License-Identifier: Apache-2.0
"""Unit tests for gabbe.hardstop."""

import time

import pytest

from gabbe.hardstop import (
    HardStop,
    HardStopTriggered,
    MaxDepthExceeded,
    MaxIterationsExceeded,
    TimeoutExceeded,
)


def test_hardstop_tick_ok():
    h = HardStop(max_iterations=5)
    h.tick()
    h.tick()
    assert h.iterations == 2


def test_hardstop_max_iterations():
    h = HardStop(max_iterations=3)
    h.tick()
    h.tick()
    h.tick()
    with pytest.raises(MaxIterationsExceeded):
        h.tick()


def test_hardstop_max_iterations_is_hard_stop_triggered():
    h = HardStop(max_iterations=1)
    h.tick()
    with pytest.raises(HardStopTriggered):
        h.tick()


def test_hardstop_max_depth():
    h = HardStop(max_depth=2)
    h.tick(depth=2)  # OK — equal
    with pytest.raises(MaxDepthExceeded):
        h.tick(depth=3)


def test_hardstop_timeout():
    h = HardStop(timeout_sec=0)  # expires immediately
    time.sleep(0.05)
    with pytest.raises(TimeoutExceeded):
        h.tick()


def test_hardstop_remaining_steps():
    h = HardStop(max_iterations=10)
    assert h.remaining_steps() == 10
    h.tick()
    assert h.remaining_steps() == 9
    h.tick()
    assert h.remaining_steps() == 8


def test_hardstop_remaining_steps_never_negative():
    h = HardStop(max_iterations=2)
    h.tick()
    h.tick()
    with pytest.raises(MaxIterationsExceeded):
        h.tick()
    assert h.remaining_steps() == 0


def test_hardstop_should_wrap_up_false():
    h = HardStop(max_iterations=10)
    assert not h.should_wrap_up(threshold=2)


def test_hardstop_should_wrap_up_true():
    h = HardStop(max_iterations=3)
    h.tick()
    h.tick()  # 2 remaining
    assert h.should_wrap_up(threshold=2)


def test_hardstop_should_wrap_up_custom_threshold():
    h = HardStop(max_iterations=5)
    h.tick()  # 4 remaining
    assert not h.should_wrap_up(threshold=3)
    h.tick()  # 3 remaining
    assert h.should_wrap_up(threshold=3)
