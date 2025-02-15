from pymongo.collection import Collection

def get_all_field_names_sync(collection: Collection) -> set[str]:
    document = collection.find_one({})
    if document is None:
        return set()
    return set(document.keys())

