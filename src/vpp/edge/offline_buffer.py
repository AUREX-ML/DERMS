"""Offline SQLite buffer for VPP telemetry messages.

Stores telemetry payloads locally when the ThingsBoard Cloud connection
is unavailable, and replays them on reconnect.
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Coroutine

import aiosqlite

from src.utils.logger import get_logger

logger = get_logger(__name__)

_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS telemetry_buffer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site_id TEXT NOT NULL,
    der_id TEXT NOT NULL,
    payload TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    forwarded INTEGER DEFAULT 0,
    retry_count INTEGER DEFAULT 0,
    created_at TEXT NOT NULL
);
"""


class OfflineBuffer:
    """Async SQLite buffer for VPP telemetry messages.

    Uses ``aiosqlite`` to persist payloads that could not be forwarded to
    ThingsBoard, then replays them when connectivity is restored.

    Args:
        db_path: Path to the SQLite database file. Defaults to ``buffer.db``.
    """

    def __init__(self, db_path: str = "buffer.db") -> None:
        self._db_path = db_path
        self._lock = asyncio.Lock()
        logger.info("OfflineBuffer initialised", extra={"db_path": db_path})

    async def _ensure_schema(self, conn: aiosqlite.Connection) -> None:
        """Create the buffer table if it does not already exist."""
        await conn.execute(_CREATE_TABLE_SQL)
        await conn.commit()

    async def store(self, payload: dict[str, Any]) -> None:
        """Persist a pending telemetry payload to the buffer.

        Args:
            payload: Validated telemetry dict containing at minimum
                ``site_id``, ``der_id``, and ``timestamp`` keys.
        """
        now = datetime.now(timezone.utc).isoformat()
        async with self._lock:
            async with aiosqlite.connect(self._db_path) as conn:
                await self._ensure_schema(conn)
                await conn.execute(
                    """
                    INSERT INTO telemetry_buffer
                        (site_id, der_id, payload, timestamp, forwarded, retry_count, created_at)
                    VALUES (?, ?, ?, ?, 0, 0, ?)
                    """,
                    (
                        payload.get("site_id", ""),
                        payload.get("der_id", ""),
                        json.dumps(payload),
                        payload.get("timestamp", now),
                        now,
                    ),
                )
                await conn.commit()
        logger.debug(
            "Payload stored in offline buffer",
            extra={"site_id": payload.get("site_id"), "der_id": payload.get("der_id")},
        )

    async def replay(
        self,
        forward_fn: Callable[[dict[str, Any]], Coroutine[Any, Any, None]],
    ) -> int:
        """Replay all pending buffered messages through ``forward_fn``.

        For each pending message the function calls ``forward_fn(payload)``.
        On success the record is marked as forwarded. On failure the
        ``retry_count`` is incremented and the record remains pending.

        Args:
            forward_fn: Async callable that accepts a payload dict and
                forwards it to ThingsBoard.

        Returns:
            Number of messages successfully replayed.
        """
        replayed = 0
        async with self._lock:
            async with aiosqlite.connect(self._db_path) as conn:
                conn.row_factory = aiosqlite.Row
                await self._ensure_schema(conn)
                async with conn.execute(
                    "SELECT * FROM telemetry_buffer WHERE forwarded = 0 ORDER BY id ASC"
                ) as cursor:
                    rows = await cursor.fetchall()

                for row in rows:
                    row_id = row["id"]
                    try:
                        payload = json.loads(row["payload"])
                        await forward_fn(payload)
                        await conn.execute(
                            "UPDATE telemetry_buffer SET forwarded = 1 WHERE id = ?",
                            (row_id,),
                        )
                        replayed += 1
                        logger.debug(
                            "Buffered message replayed",
                            extra={"buffer_id": row_id, "site_id": row["site_id"]},
                        )
                    except Exception as exc:  # noqa: BLE001
                        await conn.execute(
                            "UPDATE telemetry_buffer SET retry_count = retry_count + 1 WHERE id = ?",
                            (row_id,),
                        )
                        logger.warning(
                            "Failed to replay buffered message",
                            extra={"buffer_id": row_id, "error": str(exc)},
                        )
                await conn.commit()

        logger.info("Replay complete", extra={"replayed": replayed, "total": len(rows)})
        return replayed

    async def prune(self, max_age_hours: int = 48) -> int:
        """Delete forwarded messages older than ``max_age_hours``.

        Args:
            max_age_hours: Age threshold in hours. Defaults to 48.

        Returns:
            Number of records deleted.
        """
        cutoff = (
            datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
        ).isoformat()
        async with self._lock:
            async with aiosqlite.connect(self._db_path) as conn:
                await self._ensure_schema(conn)
                cursor = await conn.execute(
                    "DELETE FROM telemetry_buffer WHERE forwarded = 1 AND created_at < ?",
                    (cutoff,),
                )
                deleted = cursor.rowcount
                await conn.commit()
        logger.info(
            "Pruned old buffer records", extra={"deleted": deleted, "cutoff": cutoff}
        )
        return deleted

    async def pending_count(self) -> int:
        """Return the number of unforwarded messages in the buffer.

        Returns:
            Count of pending records.
        """
        async with aiosqlite.connect(self._db_path) as conn:
            await self._ensure_schema(conn)
            async with conn.execute(
                "SELECT COUNT(*) FROM telemetry_buffer WHERE forwarded = 0"
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0
