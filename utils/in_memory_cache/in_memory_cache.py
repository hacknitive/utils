from typing import Any
from logging import Logger
from datetime import datetime, timedelta
from traceback import format_exc


class InMemoryCache:

    def __init__(
            self,
            logger: Logger,
            clean_up_period_in_seconds: int,
            maximum_ttl_in_seconds: str,
            name: str,
    ) -> None:
        self.logger = logger
        self.clean_up_period_in_seconds = clean_up_period_in_seconds
        self.maximum_ttl_in_seconds = maximum_ttl_in_seconds
        self.name = name

        self.cache: dict[str, tuple[datetime, dict[str, Any]]] = dict()
        return None

    def clean_expired_items_cron_func(
        self,
    ) -> None:
        self.logger.debug("Start removing expired cache from %s", self.name)

        criteria = datetime.utcnow() + timedelta(seconds=self.clean_up_period_in_seconds)
        try:
            for key, value in self.cache.copy().items():
                if value[0] < criteria:
                    del self.cache[key]
                    self.logger.debug(
                        "This key '%s' is deleted from %s cache", 
                        key, 
                        self.name,
                        )

        except Exception:
            self.logger.warning(format_exc())

        return None

    def fetch_from_cache_without_expiration_check(
        self,
            key: str,
    ) -> dict | None:
        if key in self.cache:
            value = self.cache[key]
            return value[1]
        return None

    def fetch_from_cache_with_expiration_check(
        self,
            key: str,
    ) -> dict | None:
        if key in self.cache:
            value = self.cache[key]
            if value[0] > datetime.utcnow():
                return value[1]
        return None

    def insert_in_cache(
        self,
        key: str,
        data: str,
    ):
        self.cache[key] = (
            datetime.utcnow() + timedelta(seconds=self.maximum_ttl_in_seconds),
            data,
        )

        return None
    
    def clear_cache(self) -> None:
        self.cache.clear()
