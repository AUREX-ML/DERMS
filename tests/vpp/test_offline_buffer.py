"""Tests for OfflineBuffer — SQLite persistence and replay."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio

from src.vpp.edge.offline_buffer import OfflineBuffer


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture()
async def buf(tmp_path):
    """OfflineBuffer backed by a temporary SQLite file."""
    return OfflineBuffer(db_path=str(tmp_path / "test_buffer.db"))


SAMPLE_PAYLOAD = {
    "site_id": "site_A",
    "der_id": "bess_01",
    "der_type": "battery",
    "timestamp": "2026-05-15T10:00:00Z",
    "active_power_kw": 25.5,
    "energy_kwh": 120.0,
    "voltage_v": 400.0,
    "frequency_hz": 50.0,
    "state_of_charge": 0.78,
    "carbon_offset_kg": 12.3,
}


# ---------------------------------------------------------------------------
# store
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_store_inserts_record(buf):
    """store() inserts a pending record into the database."""
    await buf.store(SAMPLE_PAYLOAD)

    import aiosqlite
    async with aiosqlite.connect(buf._db_path) as conn:
        async with conn.execute("SELECT COUNT(*) FROM telemetry_buffer WHERE forwarded = 0") as cur:
            row = await cur.fetchone()
    assert row[0] == 1


@pytest.mark.asyncio
async def test_store_persists_payload_json(buf):
    """Stored payload round-trips through JSON correctly."""
    await buf.store(SAMPLE_PAYLOAD)

    import aiosqlite
    async with aiosqlite.connect(buf._db_path) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute("SELECT payload FROM telemetry_buffer") as cur:
            row = await cur.fetchone()
    loaded = json.loads(row["payload"])
    assert loaded["der_id"] == SAMPLE_PAYLOAD["der_id"]
    assert loaded["active_power_kw"] == SAMPLE_PAYLOAD["active_power_kw"]


# ---------------------------------------------------------------------------
# pending_count
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_pending_count_empty(buf):
    """pending_count() returns 0 for an empty buffer."""
    assert await buf.pending_count() == 0


@pytest.mark.asyncio
async def test_pending_count_after_stores(buf):
    """pending_count() reflects the number of unforwarded messages."""
    await buf.store(SAMPLE_PAYLOAD)
    await buf.store({**SAMPLE_PAYLOAD, "der_id": "inv_01"})
    assert await buf.pending_count() == 2


# ---------------------------------------------------------------------------
# replay
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_replay_calls_forward_fn_for_each_pending(buf):
    """replay() invokes forward_fn for every pending message."""
    await buf.store(SAMPLE_PAYLOAD)
    await buf.store({**SAMPLE_PAYLOAD, "der_id": "inv_01"})

    called: list[dict] = []

    async def forward_fn(payload):
        called.append(payload)

    count = await buf.replay(forward_fn)
    assert count == 2
    assert len(called) == 2


@pytest.mark.asyncio
async def test_replay_marks_forwarded_on_success(buf):
    """replay() marks records as forwarded=1 when forward_fn succeeds."""
    await buf.store(SAMPLE_PAYLOAD)

    async def forward_fn(payload):
        pass  # success

    await buf.replay(forward_fn)
    assert await buf.pending_count() == 0


@pytest.mark.asyncio
async def test_replay_increments_retry_count_on_failure(buf):
    """replay() increments retry_count and leaves record pending on failure."""
    await buf.store(SAMPLE_PAYLOAD)

    async def failing_fn(payload):
        raise RuntimeError("forward failed")

    await buf.replay(failing_fn)

    import aiosqlite
    async with aiosqlite.connect(buf._db_path) as conn:
        async with conn.execute(
            "SELECT forwarded, retry_count FROM telemetry_buffer"
        ) as cur:
            row = await cur.fetchone()

    forwarded, retry_count = row
    assert forwarded == 0
    assert retry_count == 1


@pytest.mark.asyncio
async def test_replay_returns_success_count(buf):
    """replay() returns the count of successfully forwarded messages."""
    await buf.store(SAMPLE_PAYLOAD)
    await buf.store({**SAMPLE_PAYLOAD, "der_id": "inv_01"})

    call_count = 0

    async def forward_fn(payload):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise RuntimeError("fail first")
        # second succeeds

    count = await buf.replay(forward_fn)
    assert count == 1


# ---------------------------------------------------------------------------
# prune
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_prune_deletes_old_forwarded_records(buf):
    """prune() removes forwarded records older than max_age_hours."""
    await buf.store(SAMPLE_PAYLOAD)

    # Manually mark the record as forwarded with an old created_at
    import aiosqlite
    old_time = (datetime.now(timezone.utc) - timedelta(hours=72)).isoformat()
    async with aiosqlite.connect(buf._db_path) as conn:
        await conn.execute(
            "UPDATE telemetry_buffer SET forwarded = 1, created_at = ?", (old_time,)
        )
        await conn.commit()

    deleted = await buf.prune(max_age_hours=48)
    assert deleted == 1

    async with aiosqlite.connect(buf._db_path) as conn:
        async with conn.execute("SELECT COUNT(*) FROM telemetry_buffer") as cur:
            row = await cur.fetchone()
    assert row[0] == 0


@pytest.mark.asyncio
async def test_prune_keeps_recent_forwarded_records(buf):
    """prune() retains forwarded records younger than max_age_hours."""
    await buf.store(SAMPLE_PAYLOAD)

    # Mark as forwarded but keep created_at recent (now)
    import aiosqlite
    async with aiosqlite.connect(buf._db_path) as conn:
        await conn.execute("UPDATE telemetry_buffer SET forwarded = 1")
        await conn.commit()

    deleted = await buf.prune(max_age_hours=48)
    assert deleted == 0


@pytest.mark.asyncio
async def test_prune_does_not_delete_pending_records(buf):
    """prune() never removes pending (forwarded=0) records."""
    await buf.store(SAMPLE_PAYLOAD)

    import aiosqlite
    old_time = (datetime.now(timezone.utc) - timedelta(hours=100)).isoformat()
    async with aiosqlite.connect(buf._db_path) as conn:
        await conn.execute(
            "UPDATE telemetry_buffer SET created_at = ?", (old_time,)
        )
        await conn.commit()

    deleted = await buf.prune(max_age_hours=48)
    assert deleted == 0  # pending, so not pruned
    assert await buf.pending_count() == 1
