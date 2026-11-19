from __future__ import annotations

from sqlite3 import Connection

from shared.dev_db import connect


def get_connection() -> Connection:
    return connect()
