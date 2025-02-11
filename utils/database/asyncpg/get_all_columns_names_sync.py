def get_all_columns_names_sync(
        table_name: str, 
        connection,
        ) -> set[str]:
    query = f"""
SELECT column_name
FROM information_schema.columns
WHERE table_name = '{table_name}';
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query)
        records = cursor.fetchall()
        return [record[0] for record in records]
