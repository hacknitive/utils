from datetime import datetime
from typing import (
    Iterable,
    Any,
)

from asyncpg.pool import Pool
from utils.exception_handling import ProjectBaseException
from utils.constant import (
    EnumOrderBy,
    MAP_ORDER_BY_SQL,
    EnumDatetimeDuration,
)


class DbAction:
    def __init__(
        self,
        table_name: str,
        all_columns_names: set[str],
        ilike_columns_names: set[str] = set(),
        equality_columns_names: set[str] = set(),
        range_columns_names: set[str] = set(),
    ) -> None:
        self.table_name = table_name
        self.all_columns_names = all_columns_names
        self.ilike_columns_names = ilike_columns_names
        self.equality_columns_names = equality_columns_names
        self.range_columns_names = range_columns_names

    async def insert_one(
        self,
        inputs: dict,
        postgresql_connection_pool: Pool,
        returning_fields: set[str],
    ) -> dict:
        inputs_keys_str = ", ".join(inputs.keys())
        inputs_loc_str = ", ".join([f"${i+1}" for i in range(len(inputs))])
        inputs_values = tuple(inputs.values())

        query = (
            f"""INSERT INTO {self.table_name} ({inputs_keys_str})
VALUES ({inputs_loc_str})
"""
        )

        returning_fields = self.all_columns_names & returning_fields
        if returning_fields:
            query += f'RETURNING {",".join(returning_fields)};'
        else:
            query += ';'

        return await self.connect_by_fetch_row(
            postgresql_connection_pool=postgresql_connection_pool,
            query=query,
            inputs_values=inputs_values,
        )

    async def is_exist_or_raise(
        self,
        where_clause: str,
        values: Iterable,
        postgresql_connection_pool: Pool,
        raise_on_absence: bool = False,
        exception_input: dict = dict()
    ) -> bool:

        result = await self.is_exist(
            where_clause=where_clause,
            values=values,
            postgresql_connection_pool=postgresql_connection_pool,
        )

        if result:
            return True

        if raise_on_absence:
            raise ProjectBaseException(**exception_input)
        return False

    async def is_absent_or_raise(
        self,
        where_clause: str,
        values: Iterable,
        postgresql_connection_pool: Pool,
        raise_on_existence: bool = False,
        exception_input: dict = dict()
    ) -> bool:

        result = await self.is_exist(
            where_clause=where_clause,
            values=values,
            postgresql_connection_pool=postgresql_connection_pool,
        )

        if not result:
            return True

        if raise_on_existence:
            raise ProjectBaseException(**exception_input)
        return False

    async def is_exist(
        self,
        where_clause: str,
        values: Iterable,
        postgresql_connection_pool: Pool,
    ) -> bool:

        query = (
            f"""SELECT EXISTS(
SELECT 1 FROM {self.table_name}  
WHERE {where_clause}
) As flag;"""
        )
        result = await self.connect_by_fetch_row(
            postgresql_connection_pool=postgresql_connection_pool,
            query=query,
            inputs_values=values,
        )

        return result['flag']

    async def fetch(
        self,
        where_clause: str,
        values: Iterable,
        postgresql_connection_pool: Pool,
        returning_fields: set[str],
    ) -> dict:

        returning_fields = self.all_columns_names & returning_fields
        if returning_fields:
            returning_fields_str = ",".join(returning_fields)
            query = f'SELECT {returning_fields_str}'
        else:
            query = f'SELECT *'

        query += (
            f"""
FROM {self.table_name}
WHERE {where_clause};"""
        )

        return await self.connect_by_fetch_row(
            postgresql_connection_pool=postgresql_connection_pool,
            query=query,
            inputs_values=values,
        )

    async def update(
        self,
        inputs: dict,
        where_clause: str,
        postgresql_connection_pool: Pool,
        returning_fields: set[str] = set(),
    ) -> dict | None:
        inputs = {
            **inputs,
            "updated_at": datetime.utcnow()
        }
        set_clause = [f"{key}=${index}" for index,
                      key in enumerate(inputs.keys(), start=1)]
        set_clause = ",".join(set_clause)
        query = (
            f"""UPDATE {self.table_name}
SET {set_clause}
WHERE {where_clause}"""
        )

        returning_fields = self.all_columns_names & returning_fields
        if returning_fields:
            query += f'RETURNING {",".join(returning_fields)};'
        else:
            query += ';'

        return await self.connect_by_fetch_row(
            postgresql_connection_pool=postgresql_connection_pool,
            query=query,
            inputs_values=inputs.values(),
        )

    async def paginated_fetch_by_filter(
        self,
        postgresql_connection_pool: Pool,
        returning_fields: set[str],
        current_page: int,
        page_size: int,
        kwargs: dict[str, Any]
    ) -> tuple[list[dict[str, Any]], int]:

        order_by = kwargs.pop("order_by")
        returning_fields = self.all_columns_names & returning_fields

        fetch_query = (
            f"""
SELECT {','.join(returning_fields)}
FROM {self.table_name}
"""
        )

        count_query = (
            f"""
SELECT COUNT(*) AS total_count
FROM {self.table_name}
"""
        )

        where_clause, inputs_values = self.create_where_clause(kwargs=kwargs)
        fetch_query += where_clause
        count_query += where_clause

        fetch_query += self.create_order_clause(order_by=order_by)
        fetch_query += self.create_limit_offset_clause(
            page_size=page_size,
            current_page=current_page,
        )

        records = await self.connect_by_fetch(
            postgresql_connection_pool=postgresql_connection_pool,
            query=fetch_query,
            inputs_values=inputs_values,
        )

        count = await self.connect_by_fetch(
            postgresql_connection_pool=postgresql_connection_pool,
            query=count_query,
            inputs_values=inputs_values,
        )

        return records, count[0]["total_count"]

    @staticmethod
    def remove_with_removesuffix(string: str):
        return string.removesuffix('_from').removesuffix('_to')

    def create_where_clause(
            self,
            kwargs: dict[str, list[Any]],
    ) -> tuple[str, list]:
        where_clauses = []
        inputs_values = []

        counter = 1
        for key, values in kwargs.items():
            if values:
                cleaned_key = self.remove_with_removesuffix(key)
                if cleaned_key in self.ilike_columns_names:
                    counter = self.create_where_clause_for_ilike_columns(
                        where_clauses=where_clauses,
                        values=values,
                        cleaned_key=cleaned_key,
                        counter=counter,
                        inputs_values=inputs_values,
                    )

                elif cleaned_key in self.equality_columns_names:
                    counter = self.create_where_clause_for_equality_columns(
                        where_clauses=where_clauses,
                        values=values,
                        cleaned_key=cleaned_key,
                        counter=counter,
                        inputs_values=inputs_values,
                    )

                elif cleaned_key in self.range_columns_names:
                    counter = self.create_where_clause_for_range_columns(
                        where_clauses=where_clauses,
                        values=values,
                        cleaned_key=cleaned_key,
                        counter=counter,
                        inputs_values=inputs_values,
                    )

                else:
                    continue

        if where_clauses:
            return "WHERE " + " OR ".join(where_clauses), inputs_values
        return "", inputs_values

    @staticmethod
    def create_where_clause_for_range_columns(
            where_clauses: list[str],
            key: str,
            value: int | float | datetime,
            cleaned_key: str,
            counter: int,
            inputs_values: list[Any]
    ) -> int:
        sign = ">=" if key.endswith("_from") else "<="
        where_clauses.append(f"{cleaned_key} {sign} ${counter}")
        inputs_values.append(value)
        counter += 1
        return counter

    @staticmethod
    def create_where_clause_for_equality_columns(
            where_clauses: list[str],
            values: list[Any],
            cleaned_key: str,
            counter: int,
            inputs_values: list[Any]
    ) -> int:
        or_query = list()
        for value in values:
            or_query.append(f"{cleaned_key} = ${counter}")
            inputs_values.append(value)
            counter += 1

        where_clauses.append("(" + " or ".join(or_query) + ")")
        return counter

    @staticmethod
    def create_where_clause_for_ilike_columns(
            where_clauses: list[str],
            values: list[Any],
            cleaned_key: str,
            counter: int,
            inputs_values: list[Any]
    ) -> int:
        or_query = list()
        for value in values:
            and_query = list()
            for part in value.split(" "):
                and_query.append(f"{cleaned_key} ILIKE ${counter}")
                inputs_values.append(f"%{part}%")
                counter += 1

            or_query.append(" AND ".join(and_query))

        where_clauses.append("(" + " or ".join(or_query) + ")")
        return counter

    @staticmethod
    def create_order_clause(order_by: dict[str, EnumOrderBy]) -> str:
        order_clauses = []
        if order_by:
            for column, direction in order_by.items():
                order_clauses.append(f"{column} {MAP_ORDER_BY_SQL[direction]}")

        if order_clauses:
            order_by_clause = ", ".join(order_clauses)
            return f" ORDER BY {order_by_clause} NULLS LAST"
        return ""

    @staticmethod
    def create_limit_offset_clause(
        page_size: int,
        current_page: int,
    ) -> str:
        if page_size:
            offset = (current_page - 1) * page_size
            return f" LIMIT {page_size} OFFSET {offset}"
        return ""

    @staticmethod
    async def connect_by_fetch_row(
            postgresql_connection_pool: Pool,
            query: str,
            inputs_values: Iterable = tuple(),
    ) -> Any:
        async with postgresql_connection_pool.acquire() as connection:
            return await connection.fetchrow(
                query,
                *inputs_values
            )

    @staticmethod
    async def connect_by_fetch(
            postgresql_connection_pool: Pool,
            query: str,
            inputs_values: Iterable = tuple(),
    ) -> Any:
        async with postgresql_connection_pool.acquire() as connection:
            return await connection.fetch(
                query,
                *inputs_values
            )

    async def delete(
        self,
        where_clause: str,
        values: Iterable,
        postgresql_connection_pool: Pool,
    ) -> dict:

        query = (
            f"""
DELETE FROM {self.table_name}
WHERE {where_clause};"""
        )

        return await self.connect_by_fetch_row(
            postgresql_connection_pool=postgresql_connection_pool,
            query=query,
            inputs_values=values,
        )

    async def fetch_report_on_datetime_fields(
            self,
            postgresql_connection_pool: Pool,
            duration: EnumDatetimeDuration,
            field_name: str,
    ):

        if duration == EnumDatetimeDuration.MONTHLY:
            query = (
                f"""
WITH date_range AS (
    SELECT
        DATE_TRUNC('month', MIN({field_name})) AS start_month,
        DATE_TRUNC('month', MAX({field_name})) AS end_month
    FROM
        {self.table_name}
),
months AS (
    SELECT
        generate_series(
            (SELECT start_month FROM date_range),
            (SELECT end_month FROM date_range),
            INTERVAL '1 month'
        ) AS month
)
SELECT
    to_char(months.month, 'YYYY-MM') AS datetime,
    COUNT({self.table_name}.pid) AS count
FROM
    months
LEFT JOIN
    {self.table_name} ON DATE_TRUNC('month', {self.table_name}.{field_name}) = months.month
GROUP BY
    months.month
ORDER BY
    months.month ASC;"""
            )
        else:
            query = (
                f"""
WITH date_range AS (
    SELECT
        DATE_TRUNC('day', MIN({field_name})) AS start_day,
        DATE_TRUNC('day', MAX({field_name})) AS end_day
    FROM
        {self.table_name}
),
days AS (
    SELECT
        generate_series(
            (SELECT start_day FROM date_range),
            (SELECT end_day FROM date_range),
            INTERVAL '1 day'
        ) AS day
)
SELECT
    to_char(days.day, 'YYYY-MM-DD') AS datetime,
    COUNT({self.table_name}.pid) AS count
FROM
    days
LEFT JOIN
    {self.table_name} ON DATE_TRUNC('day', {self.table_name}.{field_name}) = days.day
GROUP BY
    days.day
ORDER BY
    days.day ASC;"""
            )

        return await self.connect_by_fetch(
            postgresql_connection_pool=postgresql_connection_pool,
            query=query,
            inputs_values=tuple(),
        )
