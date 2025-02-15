from motor.motor_asyncio import AsyncIOMotorDatabase

async def get_columns_by_type(
    collection_name: str,
    db: AsyncIOMotorDatabase,
    types: set,
) -> set[str]:
    collection = db[collection_name]
    document = await collection.find_one()
    if document is None:
        return set()

    matching_fields = set()
    for key, value in document.items():
        if key == "_id":
            continue

        field_type = type(value).__name__
        if field_type in types:
            matching_fields.add(key)

    return matching_fields
