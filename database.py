import aiosqlite
import os

DB_PATH = os.environ.get("DB_PATH", "bot_data.db")


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER NOT NULL,
                chat_id INTEGER NOT NULL UNIQUE,
                chat_title TEXT,
                chat_type TEXT,
                username TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS warnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                reason TEXT,
                issued_by INTEGER NOT NULL,
                issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS bot_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                message_id INTEGER NOT NULL,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS chat_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                target_user_id INTEGER,
                performed_by INTEGER,
                details TEXT,
                occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()


async def get_user_chats(owner_id: int) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM chats WHERE owner_id = ? ORDER BY added_at DESC",
            (owner_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]


async def get_chat(chat_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM chats WHERE chat_id = ?", (chat_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def add_chat(owner_id: int, chat_id: int, chat_title: str, chat_type: str, username: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO chats (owner_id, chat_id, chat_title, chat_type, username) VALUES (?, ?, ?, ?, ?)",
            (owner_id, chat_id, chat_title, chat_type, username)
        )
        await db.commit()


async def remove_chat(owner_id: int, chat_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM chats WHERE owner_id = ? AND chat_id = ?",
            (owner_id, chat_id)
        )
        await db.commit()


async def is_chat_owner(owner_id: int, chat_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT id FROM chats WHERE owner_id = ? AND chat_id = ?",
            (owner_id, chat_id)
        ) as cursor:
            return await cursor.fetchone() is not None


async def add_warning(chat_id: int, user_id: int, reason: str, issued_by: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO warnings (chat_id, user_id, reason, issued_by) VALUES (?, ?, ?, ?)",
            (chat_id, user_id, reason, issued_by)
        )
        await db.commit()
        async with db.execute(
            "SELECT COUNT(*) FROM warnings WHERE chat_id = ? AND user_id = ?",
            (chat_id, user_id)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0


async def get_warnings(chat_id: int, user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM warnings WHERE chat_id = ? AND user_id = ?",
            (chat_id, user_id)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0


async def save_bot_message(chat_id: int, message_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO bot_messages (chat_id, message_id) VALUES (?, ?)",
            (chat_id, message_id)
        )
        await db.commit()


async def get_bot_messages(chat_id: int, limit: int = 50) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT message_id FROM bot_messages WHERE chat_id = ? ORDER BY sent_at DESC LIMIT ?",
            (chat_id, limit)
        ) as cursor:
            rows = await cursor.fetchall()
            return [r[0] for r in rows]


async def delete_bot_message_record(chat_id: int, message_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM bot_messages WHERE chat_id = ? AND message_id = ?",
            (chat_id, message_id)
        )
        await db.commit()


async def log_event(chat_id: int, event_type: str, target_user_id: int = None, performed_by: int = None, details: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO chat_events (chat_id, event_type, target_user_id, performed_by, details) VALUES (?, ?, ?, ?, ?)",
            (chat_id, event_type, target_user_id, performed_by, details)
        )
        await db.commit()


async def get_events(chat_id: int, limit: int = 20) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM chat_events WHERE chat_id = ? ORDER BY occurred_at DESC LIMIT ?",
            (chat_id, limit)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]
