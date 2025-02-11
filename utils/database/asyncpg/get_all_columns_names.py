from asyncpg import Pool


async def get_all_columns_names(
    table_name: str,
    postgresql_connection_pool: Pool,
) -> set[str]:
    query = f"""
SELECT column_name
FROM information_schema.columns
WHERE table_name = '{table_name}';
        """

    async with postgresql_connection_pool.acquire() as connection:
        records = await connection.fetch(query)

    return [record["column_name"] for record in records]
