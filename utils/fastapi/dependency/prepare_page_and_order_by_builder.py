from typing import (
    Annotated,
    Dict,
)

from fastapi import Query

from ...database.constant import (
    ORDER_BY_LITERAL,
    EnumOrderBy,
)


def prepare_page_and_order_by_builder(
        allowed_keys: set[str],
        default_page_size: int,
        default_current_page: int,
        default_order_by: str
):

    async def prepare_page_and_order_by(
        current_page: Annotated[int, Query()] = default_current_page,
        page_size: Annotated[int, Query()] = default_page_size,
        order_by: Annotated[
            str,
            Query(description='Sort order. Use comma-separated fields. Prefix with "-" for descending. e.g., "-created_at,name"'),
        ] = default_order_by,
    ) -> dict[str, int | dict[str, ORDER_BY_LITERAL]]:

        parsed_order_by: Dict[str, ORDER_BY_LITERAL] = {}

        for field in order_by.split(','):
            if not field.strip():
                continue

            if field.startswith('-'):
                parsed_order_by[field[1:]] = EnumOrderBy.D.value
            else:
                parsed_order_by[field] = EnumOrderBy.A.value

        return {
            "current_page": current_page,
            "page_size": page_size,
            "order_by": {
                k: parsed_order_by[k]
                for k
                in parsed_order_by.keys() & allowed_keys
            },
        }

    return prepare_page_and_order_by
