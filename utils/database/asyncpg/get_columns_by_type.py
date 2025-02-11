from asyncpg import Pool


async def get_columns_by_type(
    table_name: str,
    postgresql_connection_pool: Pool,
    types: set,
) -> set[str]:

    query = f"""
SELECT 
    column_name
FROM 
    information_schema.columns
WHERE 
    table_name = '{table_name}'
    AND data_type IN (
        '{"','".join(types)}'
    );"""

    async with postgresql_connection_pool.acquire() as connection:
        records = await connection.fetch(query)

    return {record["column_name"] for record in records}
