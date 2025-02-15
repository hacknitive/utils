from motor.motor_asyncio import AsyncIOMotorDatabase

async def get_all_columns_names(
    collection_name: str,
    db: AsyncIOMotorDatabase,
) -> set[str]:
    collection = db[collection_name]
    document = await collection.find_one()
    
    if document:
        return set(document.keys())
    return set()
