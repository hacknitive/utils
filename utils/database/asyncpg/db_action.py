from datetime import (
    datetime,
    UTC,
)
from typing import (
    Iterable,
    Any,
)

from asyncpg.pool import Pool
from ...exception import ProjectBaseException
from ..constant import (
    EnumOrderBy,
    MAP_ORDER_BY_SQL,
    EnumDatetimeDuration,
    VALID_DURATIONS,
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

    async def insert_many_without_transact(
        self,
        inputs_list: list[dict[str, Any]],
        postgresql_connection_pool: Pool,
        returning_fields: set[str],
    ) -> list[dict] | str:
        batch_size = self.calculate_batch_size(inputs_list=inputs_list)
        batches = self.build_batches(
            inputs_list=inputs_list,
            batch_size=batch_size,
        )

        total_results = list()
        for batch in batches:
            query, inputs_values = await self._build_query_for_insert_many(
                batch=batch,
                returning_fields=returning_fields,
            )

            results = await self._connect_by_fetch(
                postgresql_connection_pool=postgresql_connection_pool,
                query=query,
                inputs_values=inputs_values,
            )
            total_results.extend(results)

        return total_results

    async def insert_many_with_transact(
        self,
        inputs_list: list[dict[str, Any]],
        postgresql_connection_pool: Pool,
        returning_fields: set[str],
    ) -> list[dict] | str:
        batch_size = self.calculate_batch_size(inputs_list=inputs_list)
        batches = self.build_batches(
            inputs_list=inputs_list,
            batch_size=batch_size,
        )

        return await self._connect_by_fetch_for_insert_many_with_transact(
            postgresql_connection_pool=postgresql_connection_pool,
            batches=batches,
            returning_fields=returning_fields,
        )

    async def _connect_by_fetch_for_insert_many_with_transact(
            self,
            postgresql_connection_pool: Pool,
            batches: list[list[dict[str, Any]]],
            returning_fields: set[str],
    ) -> Any:
        total_results = list()
        async with postgresql_connection_pool.acquire() as connection:
            async with connection.transaction():
                for batch in batches:
                    query, inputs_values = await self._build_query_for_insert_many(
                        batch=batch,
                        returning_fields=returning_fields,
                    )
                    results = await connection.fetch(query, *inputs_values)
                    total_results.extend(results)

        return total_results

    @staticmethod
    def calculate_batch_size(inputs_list: list[dict[str, Any]]) -> int:
        maximum_key_count = max([len(i) for i in inputs_list])
        # asyncpg only accept 32767 argument in a single query
        return int(30000 / maximum_key_count)

    @staticmethod
    def build_batches(
            inputs_list: list[dict[str, Any]],
            batch_size: int,
    ) -> list[list[dict[str, Any]]]:
        return [
            inputs_list[i:i+batch_size]
            for i in range(
                0,
                len(inputs_list),
                batch_size,
            )
        ]

    async def _build_query_for_insert_many(
            self,
            batch: list[dict],
            returning_fields: set[str],
    ) -> tuple[str, list]:
        columns = list(batch[0].keys())
        columns_str = ", ".join(columns)

        row_placeholders_list = []
        inputs_values = []
        num_columns = len(columns)
        for i, row in enumerate(batch):
            placeholders = []
            for j, col in enumerate(columns):
                placeholder = f"${i * num_columns + j + 1}"
                placeholders.append(placeholder)
                inputs_values.append(row[col])
            row_placeholders = "(" + ", ".join(placeholders) + ")"
            row_placeholders_list.append(row_placeholders)

        values_placeholders_str = ", ".join(row_placeholders_list)
        query = f"INSERT INTO {self.table_name} ({columns_str}) VALUES {values_placeholders_str}"
        valid_returning_fields = self.all_columns_names & returning_fields
        if valid_returning_fields:
            query += f" RETURNING {','.join(valid_returning_fields)};"
        else:
            query += ";"

        return query, inputs_values

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

        return await self._connect_by_fetch_row(
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
        result = await self._connect_by_fetch_row(
            postgresql_connection_pool=postgresql_connection_pool,
            query=query,
            inputs_values=values,
        )

        return result['flag']

    def _prepare_fetch_query(
        self,
        where_clause: str,
        returning_fields: set[str],
        order_by: dict[str, EnumOrderBy],
        current_page: int,
        page_size: int,
    ) -> str:

        returning_fields = self.all_columns_names & returning_fields
        if returning_fields:
            returning_fields_str = ",".join(returning_fields)
            query = f'SELECT {returning_fields_str}'
        else:
            query = f'SELECT *'

        query += (
            f"""
FROM {self.table_name}
WHERE {where_clause}"""
        )

        query += self._create_order_clause(order_by=order_by)
        query += self._create_limit_offset_clause(
            page_size=page_size,
            current_page=current_page,
        )

        return query + ";"

    async def fetch(
        self,
        where_clause: str,
        values: Iterable,
        postgresql_connection_pool: Pool,
        returning_fields: set[str],
        order_by: dict[str, EnumOrderBy] = dict(),
        current_page: int = 1,
        page_size: int = 0,
    ) -> dict:

        query = self._prepare_fetch_query(
            where_clause=where_clause,
            returning_fields=returning_fields,
            order_by=order_by,
            current_page=current_page,
            page_size=page_size,
        )

        return await self._connect_by_fetch_row(
            postgresql_connection_pool=postgresql_connection_pool,
            query=query,
            inputs_values=values,
        )

    async def fetch_many(
        self,
        where_clause: str,
        values: Iterable,
        postgresql_connection_pool: Pool,
        returning_fields: set[str],
        order_by: dict[str, EnumOrderBy] = dict(),
        current_page: int = 1,
        page_size: int = 0,
    ) -> list[dict]:

        query = self._prepare_fetch_query(
            where_clause=where_clause,
            returning_fields=returning_fields,
            order_by=order_by,
            current_page=current_page,
            page_size=page_size,
        )

        return await self._connect_by_fetch(
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
        direct_set_clause: list[str] = list(),
        add_updated_at: bool = True,
    ) -> dict | None:
        if add_updated_at:
            inputs = {
                **inputs,
                "updated_at": datetime.now(tz=UTC)
            }

        set_clause = [f"{key}=${index}" for index,
                      key in enumerate(inputs.keys(), start=1)]

        if direct_set_clause:
            set_clause.extend(direct_set_clause)

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

        return await self._connect_by_fetch_row(
            postgresql_connection_pool=postgresql_connection_pool,
            query=query,
            inputs_values=inputs.values(),
        )

    async def count(
        self,
        postgresql_connection_pool: Pool,
        where_clause: str,
        values: Iterable,
    ) -> int:
        count_query = f"SELECT COUNT(*) AS total_count FROM {self.table_name} WHERE {where_clause}"

        count_result = await self._connect_by_fetch_row(
            postgresql_connection_pool=postgresql_connection_pool,
            query=count_query,
            inputs_values=values,
        )

        return count_result["total_count"] if count_result else 0

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

        where_clause, inputs_values = self._create_where_clause(kwargs=kwargs)
        fetch_query += where_clause
        count_query += where_clause

        fetch_query += self._create_order_clause(order_by=order_by)
        fetch_query += self._create_limit_offset_clause(
            page_size=page_size,
            current_page=current_page,
        )

        records = await self._connect_by_fetch(
            postgresql_connection_pool=postgresql_connection_pool,
            query=fetch_query,
            inputs_values=inputs_values,
        )

        count = await self._connect_by_fetch(
            postgresql_connection_pool=postgresql_connection_pool,
            query=count_query,
            inputs_values=inputs_values,
        )

        return records, count[0]["total_count"]

    @staticmethod
    def _remove_with_removesuffix(string: str):
        return string.removesuffix('_from').removesuffix('_to')

    def _create_where_clause(
            self,
            kwargs: dict[str, list[Any]],
    ) -> tuple[str, list]:
        where_clauses = []
        inputs_values = []

        counter = 1
        for key, values in kwargs.items():
            if values:  # TODO: Use sentinel
                cleaned_key = self._remove_with_removesuffix(key)
                if cleaned_key in self.ilike_columns_names:
                    counter = self._create_where_clause_for_ilike_columns(
                        where_clauses=where_clauses,
                        values=values,
                        cleaned_key=cleaned_key,
                        counter=counter,
                        inputs_values=inputs_values,
                    )

                elif cleaned_key in self.equality_columns_names:
                    counter = self._create_where_clause_for_equality_columns(
                        where_clauses=where_clauses,
                        values=values,
                        cleaned_key=cleaned_key,
                        counter=counter,
                        inputs_values=inputs_values,
                    )

                elif cleaned_key in self.range_columns_names:
                    counter = self._create_where_clause_for_range_columns(
                        where_clauses=where_clauses,
                        values=values,
                        key=key,
                        cleaned_key=cleaned_key,
                        counter=counter,
                        inputs_values=inputs_values,
                    )

                else:
                    continue

        if where_clauses:
            return "WHERE " + " AND ".join(where_clauses), inputs_values
        return "", inputs_values

    @staticmethod
    def _create_where_clause_for_range_columns(
            where_clauses: list[str],
            key: str,
            values: int | float | datetime,
            cleaned_key: str,
            counter: int,
            inputs_values: list[Any]
    ) -> int:
        sign = ">=" if key.endswith("_from") else "<="
        where_clauses.append(f"{cleaned_key} {sign} ${counter}")
        inputs_values.append(values)
        counter += 1
        return counter

    @staticmethod
    def _create_where_clause_for_equality_columns(
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

        where_clauses.append("(" + " OR ".join(or_query) + ")")
        return counter

    @staticmethod
    def _create_where_clause_for_ilike_columns(
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

        where_clauses.append("(" + " OR ".join(or_query) + ")")
        return counter

    @staticmethod
    def _create_order_clause(order_by: dict[str, EnumOrderBy]) -> str:
        order_clauses = []
        if order_by:
            for column, direction in order_by.items():
                order_clauses.append(f"{column} {MAP_ORDER_BY_SQL[direction]}")

        if order_clauses:
            order_by_clause = ", ".join(order_clauses)
            return f" ORDER BY {order_by_clause} NULLS LAST"
        return ""

    @staticmethod
    def _create_limit_offset_clause(
        page_size: int,
        current_page: int,
    ) -> str:
        if page_size:
            offset = (current_page - 1) * page_size
            return f" LIMIT {page_size} OFFSET {offset}"
        return ""

    @staticmethod
    async def _connect_by_fetch_row(
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
    async def _connect_by_fetch(
            postgresql_connection_pool: Pool,
            query: str,
            inputs_values: Iterable = tuple(),
    ) -> Any:
        async with postgresql_connection_pool.acquire() as connection:
            return await connection.fetch(
                query,
                *inputs_values,
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

        return await self._connect_by_fetch_row(
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

        trunc_value, date_format = VALID_DURATIONS[duration]

        query = (
            f"""
WITH date_range AS (
    SELECT
        DATE_TRUNC('{trunc_value}', MIN({field_name})) AS start_range,
        DATE_TRUNC('{trunc_value}', MAX({field_name})) AS end_range
    FROM
        {self.table_name}
),
periods AS (
    SELECT
        generate_series(
            (SELECT start_range FROM date_range),
            (SELECT end_range FROM date_range),
            INTERVAL '1 {trunc_value}'
        ) AS period
)
SELECT
    to_char(periods.period, '{date_format}') AS datetime,
    COUNT({self.table_name}.pid) AS count
FROM
    periods
LEFT JOIN
    {self.table_name} ON DATE_TRUNC('{trunc_value}', {self.table_name}.{field_name}) = periods.period
GROUP BY
    periods.period
ORDER BY
    periods.period ASC;""")

        return await self._connect_by_fetch(
            postgresql_connection_pool=postgresql_connection_pool,
            query=query,
            inputs_values=tuple(),
        )

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

        order_by: dict = kwargs.pop("order_by")
        group_by_on_fields = self.all_columns_names & group_by_on_fields
        group_by_on_fields_str = ','.join(group_by_on_fields)

        fetch_query = (
            f"""
SELECT {group_by_on_fields_str}, {aggregation_in_select}
FROM {self.table_name}
"""
        )

        where_clause, inputs_values = self._create_where_clause(kwargs=kwargs)
        fetch_query += where_clause

        fetch_query += (
            f"""\nGROUP BY {group_by_on_fields_str}"""
        )

        order_by = {key: value for key, value in order_by.items(
        ) if key in {*group_by_on_fields, *aggregation_variable_name}}
        fetch_query += self._create_order_clause(order_by=order_by)
        fetch_query += self._create_limit_offset_clause(
            page_size=page_size,
            current_page=current_page,
        )

        records = await self._connect_by_fetch(
            postgresql_connection_pool=postgresql_connection_pool,
            query=fetch_query,
            inputs_values=inputs_values,
        )

        return records
