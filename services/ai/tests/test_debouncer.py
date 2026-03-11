"""Tests for the Debouncer (US-004).

Test IDs:
  T-2.10.01 — Debounce waits period before processing.
  T-2.10.02 — Debounce resets on new message (two messages → one execution).
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from events.publishers import clear_published_events, get_published_events
from processing.debouncer import Debouncer, DebouncerState


@pytest.fixture(autouse=True)
def _clear_events():
    """Clear published events before each test."""
    clear_published_events()
    yield
    clear_published_events()


def _make_debouncer(
    timer: float = 0.1,
    pipeline_callback: AsyncMock | None = None,
) -> Debouncer:
    """Create a Debouncer with a short timer and mock core client."""
    core_client = MagicMock()
    core_client.get_admin_parameter.return_value = {"value": str(timer)}
    callback = pipeline_callback or AsyncMock()
    return Debouncer(pipeline_callback=callback, core_client=core_client), callback


# ── T-2.10.01: Debounce waits period ──


@pytest.mark.asyncio
async def test_debounce_waits_period():
    """T-2.10.01: Processing triggers only after debounce_timer expires."""
    debouncer, callback = _make_debouncer(timer=0.1)

    await debouncer.start("idea-1")

    # Immediately after start, should be debouncing
    assert debouncer.get_state("idea-1") == DebouncerState.DEBOUNCING
    assert callback.call_count == 0

    # Wait for timer to expire + small buffer
    await asyncio.sleep(0.2)

    # Pipeline should have been called exactly once
    callback.assert_awaited_once_with("idea-1")
    # State should return to idle after processing
    assert debouncer.get_state("idea-1") == DebouncerState.IDLE


@pytest.mark.asyncio
async def test_debounce_publishes_debouncing_event():
    """start() publishes ai.processing {state: debouncing}."""
    debouncer, _callback = _make_debouncer(timer=0.1)

    await debouncer.start("idea-1")

    events = get_published_events()
    debouncing_events = [
        e for e in events
        if e["event_type"] == "ai.processing" and e.get("state") == "debouncing"
    ]
    assert len(debouncing_events) == 1
    assert debouncing_events[0]["idea_id"] == "idea-1"

    # Cleanup
    debouncer.cancel("idea-1")


@pytest.mark.asyncio
async def test_debounce_state_transitions():
    """State transitions: idle → debouncing → processing → idle."""
    debouncer, callback = _make_debouncer(timer=0.1)

    # Initially idle
    assert debouncer.get_state("idea-1") == DebouncerState.IDLE

    # After start: debouncing
    await debouncer.start("idea-1")
    assert debouncer.get_state("idea-1") == DebouncerState.DEBOUNCING

    # After timer expires: processing then idle
    await asyncio.sleep(0.2)
    callback.assert_awaited_once()
    assert debouncer.get_state("idea-1") == DebouncerState.IDLE


# ── T-2.10.02: Debounce resets on new message ──


@pytest.mark.asyncio
async def test_debounce_resets_on_new_message():
    """T-2.10.02: Two messages 50ms apart → one execution after timer."""
    debouncer, callback = _make_debouncer(timer=0.15)

    # First message
    await debouncer.start("idea-1")
    assert callback.call_count == 0

    # Second message 50ms later (resets timer)
    await asyncio.sleep(0.05)
    await debouncer.reset("idea-1")
    assert callback.call_count == 0

    # Wait for original timer to have expired (but reset pushed it forward)
    await asyncio.sleep(0.12)
    assert callback.call_count == 0, "Should not have fired yet after reset"

    # Wait for the reset timer to expire
    await asyncio.sleep(0.1)
    callback.assert_awaited_once_with("idea-1")


@pytest.mark.asyncio
async def test_debounce_reset_publishes_new_debouncing_event():
    """reset() publishes another ai.processing {state: debouncing} event."""
    debouncer, _callback = _make_debouncer(timer=0.5)

    await debouncer.start("idea-1")
    await debouncer.reset("idea-1")

    events = get_published_events()
    debouncing_events = [
        e for e in events
        if e["event_type"] == "ai.processing" and e.get("state") == "debouncing"
    ]
    # Two events: one from start, one from reset
    assert len(debouncing_events) == 2

    # Cleanup
    debouncer.cancel("idea-1")


# ── Cancel ──


@pytest.mark.asyncio
async def test_cancel_returns_to_idle():
    """cancel() stops the timer and returns state to idle."""
    debouncer, callback = _make_debouncer(timer=0.1)

    await debouncer.start("idea-1")
    debouncer.cancel("idea-1")

    assert debouncer.get_state("idea-1") == DebouncerState.IDLE

    # Wait past the timer — callback should NOT fire
    await asyncio.sleep(0.2)
    callback.assert_not_awaited()


# ── Admin param fallback ──


@pytest.mark.asyncio
async def test_debounce_timer_fallback_default():
    """Uses default 3s when admin param is empty."""
    core_client = MagicMock()
    core_client.get_admin_parameter.return_value = {"value": ""}
    debouncer = Debouncer(pipeline_callback=AsyncMock(), core_client=core_client)

    timer = debouncer._get_debounce_timer()
    assert timer == 3.0


# ── Cleanup ──


@pytest.mark.asyncio
async def test_cleanup_removes_state():
    """cleanup() removes all per-idea state."""
    debouncer, _callback = _make_debouncer(timer=0.5)

    await debouncer.start("idea-1")
    debouncer.cleanup("idea-1")

    assert debouncer.get_state("idea-1") == DebouncerState.IDLE
    assert "idea-1" not in debouncer.states


# ── Pipeline callback error handling ──


@pytest.mark.asyncio
async def test_pipeline_error_returns_to_idle():
    """If pipeline_callback raises, state still returns to idle."""
    callback = AsyncMock(side_effect=RuntimeError("pipeline failed"))
    debouncer, _ = _make_debouncer(timer=0.05, pipeline_callback=callback)

    await debouncer.start("idea-1")
    await asyncio.sleep(0.15)

    callback.assert_awaited_once()
    assert debouncer.get_state("idea-1") == DebouncerState.IDLE
