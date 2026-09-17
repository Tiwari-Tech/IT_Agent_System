import asyncio

from sqlalchemy import text

from backend.db.database import get_engine


async def main() -> None:
    async with get_engine().connect() as conn:
        rows = (
            await conn.execute(
                text(
                    "select column_name from information_schema.columns "
                    "where table_name = 'users' order by ordinal_position"
                )
            )
        ).scalars().all()
        print(rows)


asyncio.run(main())
