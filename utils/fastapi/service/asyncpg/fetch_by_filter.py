from typing import Type

from asyncpg import Pool
from pydantic import BaseModel

from utils.database.asyncpg import DbAction


async def fetch_by_filter(
    postgresql_connection_pool: Pool,
    inclusion: set[str],
    current_page: int,
    page_size: int,
    db_action: DbAction,
    response_model: Type[BaseModel],
    kwargs: dict,
) -> dict:
    records, total = await db_action.paginated_fetch_by_filter(
        postgresql_connection_pool=postgresql_connection_pool,
        returning_fields=inclusion,
        current_page=current_page,
        page_size=page_size,
        kwargs=kwargs,
    )

    return {
        "pagination": {
            "current_page": current_page,
            "page_size": page_size,
            "total": total,
        },
        "data": [response_model(**record).model_dump(include=inclusion) for record in records]
    }
