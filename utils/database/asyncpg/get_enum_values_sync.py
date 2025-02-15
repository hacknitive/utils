from asyncpg import Pool


def get_enum_values_sync(
        enum_name: str, 
        connection,
)-> set[str]:
    query = f"""
SELECT unnest(enum_range(NULL::{enum_name})) AS result;
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query)
        records = cursor.fetchall()
        return {record[0] for record in records}
