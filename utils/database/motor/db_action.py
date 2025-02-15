from datetime import datetime
from typing import (
    Any,
    Optional,
    Dict,
    List,
    Set,
    Tuple,
)

from pymongo import ReturnDocument
from motor import MotorCollection

from ...exception_handling import ProjectBaseException
from ..constant import (
    EnumOrderBy,
    MAP_ORDER_BY_MQL,
    EnumDatetimeDuration,
)


class DbAction:
    def __init__(
        self,
        collection_name: MotorCollection,
        all_fields: Set[str],
        ilike_fields: Set[str] = set(),
        equality_fields: Set[str] = set(),
        range_fields: Set[str] = set(),
    ) -> None:
        self.collection_name = collection_name
        self.all_fields = all_fields
        self.ilike_fields = ilike_fields
        self.equality_fields = equality_fields
        self.range_fields = range_fields

    async def insert_one(
        self,
        inputs: dict,
        returning_fields: Set[str],
    ) -> dict:
        result = await self.mongodb_collection.insert_one(inputs)
        filtered_fields = self.all_fields & returning_fields
        if filtered_fields:
            projection = {field: 1 for field in filtered_fields}
            doc = await self.mongodb_collection.find_one(
                {"_id": result.inserted_id},
                projection=projection,
            )
            return doc
        else:
            return {"inserted_id": result.inserted_id}

    async def is_exist_or_raise(
        self,
        filter: dict,

        raise_on_absence: bool = False,
        exception_input: dict = {},
    ) -> bool:
        result = await self.is_exist(filter)
        if result:
            return True
        if raise_on_absence:
            raise ProjectBaseException(**exception_input)
        return False

    async def is_absent_or_raise(
        self,
        filter: dict,

        raise_on_existence: bool = False,
        exception_input: dict = {},
    ) -> bool:
        result = await self.is_exist(filter)
        if not result:
            return True
        if raise_on_existence:
            raise ProjectBaseException(**exception_input)
        return False

    async def is_exist(
        self,
        filter: dict,

    ) -> bool:
        doc = await self.mongodb_collection.find_one(filter, projection={"_id": 1})
        return doc is not None

    async def fetch(
        self,
        filter: dict,

        returning_fields: Set[str],
    ) -> Optional[dict]:
        filtered_fields = self.all_fields & returning_fields
        projection = {
            field: 1 for field in filtered_fields} if filtered_fields else None
        doc = await self.mongodb_collection.find_one(filter, projection=projection)
        return doc

    async def update(
        self,
        inputs: dict,
        filter: dict,

        returning_fields: Set[str] = set(),
    ) -> Optional[dict]:
        """
        Updates a document (adds/updates the 'updated_at' field) and returns the modified document.
        """
        inputs = {
            **inputs,
            "updated_at": datetime.utcnow()
        }
        filtered_fields = self.all_fields & returning_fields
        projection = {
            field: 1 for field in filtered_fields} if filtered_fields else None
        updated_doc = await self.mongodb_collection.find_one_and_update(
            filter,
            {"$set": inputs},
            return_document=ReturnDocument.AFTER,
            projection=projection,
        )
        return updated_doc

    async def paginated_fetch_by_filter(
        self,

        returning_fields: Set[str],
        current_page: int,
        page_size: int,
        kwargs: Dict[str, Any]
    ) -> Tuple[List[dict], int]:
        """
        Fetches documents by building a MongoDB filter based on kwargs.
        Supports ordering (via an 'order_by' key in kwargs), and pagination (skip/limit).
        Returns a tuple of (records, total_count).
        """
        order_by = kwargs.pop("order_by", {})
        projection = {field: 1 for field in (
            self.all_fields & returning_fields)} if returning_fields else None
        filter_dict = self.create_filter(kwargs)

        sort_list = self.create_order_clause(order_by)

        cursor = self.mongodb_collection.find(filter_dict, projection=projection)
        if sort_list:
            cursor = cursor.sort(sort_list)
        if page_size:
            skip_amount = (current_page - 1) * page_size
            cursor = cursor.skip(skip_amount).limit(page_size)
        records = await cursor.to_list(length=page_size)
        count = await self.mongodb_collection.count_documents(filter_dict)
        return records, count

    @staticmethod
    def remove_with_removesuffix(string: str) -> str:
        return string.removesuffix('_from').removesuffix('_to')

    def create_filter(self, kwargs: Dict[str, List[Any]]) -> dict:
        filters = []
        for key, values in kwargs.items():
            if not values:
                continue
            cleaned_key = self.remove_with_removesuffix(key)
            if cleaned_key in self.ilike_fields:
                condition = self.create_filter_for_ilike_column(
                    cleaned_key, values)
                if condition:
                    filters.append(condition)
            elif cleaned_key in self.equality_fields:
                condition = self.create_filter_for_equality_column(
                    cleaned_key, values)
                if condition:
                    filters.append(condition)
            elif cleaned_key in self.range_fields:
                for value in values:
                    condition = self.create_filter_for_range_column(key, value)
                    if condition:
                        filters.append(condition)
            else:
                continue
        if filters:
            if len(filters) == 1:
                return filters[0]
            else:
                return {"$or": filters}
        return {}

    @staticmethod
    def create_filter_for_range_column(key: str, value: int | float | datetime) -> dict:
        if key.endswith("_from"):
            cleaned_key = key.removesuffix('_from')
            return {cleaned_key: {"$gte": value}}
        elif key.endswith("_to"):
            cleaned_key = key.removesuffix('_to')
            return {cleaned_key: {"$lte": value}}
        return {}

    @staticmethod
    def create_filter_for_equality_column(cleaned_key: str, values: List[Any]) -> dict:
        # Use the $in operator to match any of the provided values.
        return {cleaned_key: {"$in": values}}

    @staticmethod
    def create_filter_for_ilike_column(cleaned_key: str, values: List[str]) -> dict:
        """
        Converts each value into a regex condition (split on spaces and combine with $and)
        and then combines multiple values with $or.
        """
        or_conditions = []
        for value in values:
            parts = value.split(" ")
            and_conditions = []
            for part in parts:
                and_conditions.append(
                    {cleaned_key: {"$regex": f".*{part}.*", "$options": "i"}})
            if and_conditions:
                if len(and_conditions) > 1:
                    or_conditions.append({"$and": and_conditions})
                else:
                    or_conditions.append(and_conditions[0])
        if or_conditions:
            if len(or_conditions) == 1:
                return or_conditions[0]
            else:
                return {"$or": or_conditions}
        return {}

    @staticmethod
    def create_order_clause(order_by: Dict[str, EnumOrderBy]) -> List[tuple]:
        sort_list = []
        if order_by:
            for field, direction in order_by.items():
                sort_list.append((field, MAP_ORDER_BY_MQL[direction]))
        return sort_list

    async def delete(
        self,
        filter: dict,

    ) -> dict:
        result = await self.mongodb_collection.delete_one(filter)
        return {"deleted_count": result.deleted_count}

    async def fetch_report_on_datetime_fields(
        self,

        duration: EnumDatetimeDuration,
        field_name: str,
    ):
        if duration == EnumDatetimeDuration.MONTHLY:
            pipeline = [
                {
                    "$group": {
                        "_id": {"$dateTrunc": {"date": f"${field_name}", "unit": "month"}},
                        "count": {"$sum": 1}
                    }
                },
                {"$sort": {"_id": 1}},
                {
                    "$project": {
                        "datetime": {"$dateToString": {"format": "%Y-%m", "date": "$_id"}},
                        "count": 1,
                        "_id": 0
                    }
                }
            ]
        else:
            pipeline = [
                {
                    "$group": {
                        "_id": {"$dateTrunc": {"date": f"${field_name}", "unit": "day"}},
                        "count": {"$sum": 1}
                    }
                },
                {"$sort": {"_id": 1}},
                {
                    "$project": {
                        "datetime": {"$dateToString": {"format": "%Y-%m-%d", "date": "$_id"}},
                        "count": 1,
                        "_id": 0
                    }
                }
            ]
        cursor = self.mongodb_collection.aggregate(pipeline)
        result = await cursor.to_list(length=None)
        return result
