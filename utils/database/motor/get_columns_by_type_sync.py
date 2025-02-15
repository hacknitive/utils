from pymongo.collection import Collection
from typing import Set, Any, Dict

def get_columns_by_type_sync(
        collection: Collection, 
        types: Set[str],
        ) -> Set[str]:
    document: Dict[str, Any] = collection.find_one({})
    if document is None:
        return set()

    return {key for key, value in document.items() if type(value).__name__ in types}
