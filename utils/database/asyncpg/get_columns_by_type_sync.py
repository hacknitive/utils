def get_columns_by_type_sync(
        table_name: str, 
        connection,
        types: set,
)-> set[str]:
    query = f"""
SELECT 
    column_name
FROM 
    information_schema.columns
WHERE 
    table_name = '{table_name}'
    AND data_type IN ('{"','".join(types)}');
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query)
        records = cursor.fetchall()
        return {record[0] for record in records}
    