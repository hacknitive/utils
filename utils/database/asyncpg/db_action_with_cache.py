from typing import (
    Iterable,
    Any,
)

from asyncpg.pool import Pool
from ...cache import InMemoryCacheManager
from ..constant import (
    EnumDatetimeDuration,
)

from .db_action import DbAction


class DbActionWithCache(DbAction):
    def __init__(
        self,
        table_name: str,
        all_columns_names: set[str],
        cache_manager: InMemoryCacheManager,
        ilike_columns_names: set[str] = set(),
        equality_columns_names: set[str] = set(),
        range_columns_names: set[str] = set(),
    ) -> None:
        self.cache_manager = cache_manager

        return super().__init__(
            table_name=table_name,
            all_columns_names=all_columns_names,
            ilike_columns_names=ilike_columns_names,
            equality_columns_names=equality_columns_names,
            range_columns_names=range_columns_names,
        )

    async def insert_many_without_transact(
        self,
        inputs_list: list[dict[str, Any]],
        postgresql_connection_pool: Pool,
        returning_fields: set[str],
    ) -> list[dict] | str:
        records = await super().insert_many_without_transact(
            inputs_list=inputs_list,
            postgresql_connection_pool=postgresql_connection_pool,
            returning_fields=returning_fields,
        )
        self.cache_manager.clear_cache()
        return records


    async def insert_many_with_transact(
        self,
        inputs_list: list[dict[str, Any]],
        postgresql_connection_pool: Pool,
        returning_fields: set[str],
    ) -> list[dict] | str:
        records = await super().insert_many_with_transact(
            inputs_list=inputs_list,
            postgresql_connection_pool=postgresql_connection_pool,
            returning_fields=returning_fields,
        )
        self.cache_manager.clear_cache()
        return records

    async def insert_one(
        self,
        inputs: dict,
        postgresql_connection_pool: Pool,
        returning_fields: set[str],
    ) -> dict:
        records = await super().insert_one(
            inputs=inputs,
            postgresql_connection_pool=postgresql_connection_pool,
            returning_fields=returning_fields,
        )
        self.cache_manager.clear_cache()
        return records


    async def fetch(
        self,
        where_clause: str,
        values: Iterable,
        postgresql_connection_pool: Pool,
        returning_fields: set[str],
    ) -> dict:
        key = f"{self.table_name}:fetch:{where_clause}:{values}:{returning_fields}"
        value = self.cache_manager.fetch_from_cache_without_expiration_check(
            key=key
        )
        if value:
            return value
        
        records = await super().fetch(
            where_clause=where_clause,
            values=values,
            postgresql_connection_pool=postgresql_connection_pool,
            returning_fields=returning_fields,
        )

        self.cache_manager.insert_in_cache_without_expiration(
            key=key,
            value=records,
        )

        return records

    async def fetch_many(
        self,
        where_clause: str,
        values: Iterable,
        postgresql_connection_pool: Pool,
        returning_fields: set[str],
    ) -> list[dict]:
        key = f"{self.table_name}:fetch_many:{where_clause}:{values}:{returning_fields}"
        value = self.cache_manager.fetch_from_cache_without_expiration_check(
            key=key
        )
        if value:
            return value
        
        records = await super().fetch_many(
            where_clause=where_clause,
            values=values,
            postgresql_connection_pool=postgresql_connection_pool,
            returning_fields=returning_fields,
        )

        self.cache_manager.insert_in_cache_without_expiration(
            key=key,
            value=records,
        )

        return records

    async def update(
        self,
        inputs: dict,
        where_clause: str,
        postgresql_connection_pool: Pool,
        returning_fields: set[str] = set(),
    ) -> dict | None:
        records = await super().update(
            inputs=inputs,
            where_clause=where_clause,
            postgresql_connection_pool=postgresql_connection_pool,
            returning_fields=returning_fields,
        )
        self.cache_manager.clear_cache()
        return records

    async def paginated_fetch_by_filter(
        self,
        postgresql_connection_pool: Pool,
        returning_fields: set[str],
        current_page: int,
        page_size: int,
        kwargs: dict[str, Any]
    ) -> tuple[list[dict[str, Any]], int]:
        key = f"{self.table_name}:paginated_fetch_by_filter:{returning_fields}:{current_page}:{page_size}:{kwargs}"
        value = self.cache_manager.fetch_from_cache_without_expiration_check(
            key=key
        )
        if value:
            return value
        
        records = await super().paginated_fetch_by_filter(
            current_page=current_page,
            page_size=page_size,
            kwargs=kwargs,
            postgresql_connection_pool=postgresql_connection_pool,
            returning_fields=returning_fields,
        )

        self.cache_manager.insert_in_cache_without_expiration(
            key=key,
            value=records,
        )

        return records


    async def delete(
        self,
        where_clause: str,
        values: Iterable,
        postgresql_connection_pool: Pool,
    ) -> dict:
        records = await super().delete(
            where_clause=where_clause,
            values=values,
            postgresql_connection_pool=postgresql_connection_pool,
        )
        self.cache_manager.clear_cache()
        return records

    async def fetch_report_on_datetime_fields(
            self,
            postgresql_connection_pool: Pool,
            duration: EnumDatetimeDuration,
            field_name: str,
    ):
        key = f"{self.table_name}:fetch_report_on_datetime_fields:{duration}:{field_name}"
        value = self.cache_manager.fetch_from_cache_without_expiration_check(
            key=key
        )
        if value:
            return value
        
        records = await super().fetch_report_on_datetime_fields(
            duration=duration,
            field_name=field_name,
            postgresql_connection_pool=postgresql_connection_pool,
        )

        self.cache_manager.insert_in_cache_without_expiration(
            key=key,
            value=records,
        )

        return records

    async def filter_then_aggregate(
        self,
        postgresql_connection_pool: Pool,
        group_by_on_fields: set[str],
        current_page: int,
        page_size: int,
        kwargs: dict[str, Any],
        aggregation_in_select: str, 
        aggregation_variable_name: set[str], 
    ) -> list[dict[str, Any]]:
        key = f"{self.table_name}:filter_then_aggregate:{group_by_on_fields}:{current_page}:{page_size}:{kwargs}:{aggregation_in_select}"
        value = self.cache_manager.fetch_from_cache_without_expiration_check(key=key)
        if value:
            return value

        records = await super().filter_then_aggregate(
            postgresql_connection_pool=postgresql_connection_pool,
            group_by_on_fields=group_by_on_fields,
            current_page=current_page,
            page_size=page_size,
            kwargs=kwargs,
            aggregation_in_select=aggregation_in_select, 
            aggregation_variable_name=aggregation_variable_name, 
        )

        self.cache_manager.insert_in_cache_without_expiration(
            key=key,
            value=records,
        )

        return records