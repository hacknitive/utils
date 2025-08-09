import asyncio
import json
from logging import Logger, getLogger

from redis.asyncio import ConnectionPool, Redis
from redis.exceptions import ConnectionError, RedisError


class AsyncRedisClient:
    """
    An asyncio-enabled Redis client wrapper with connection pooling,
    logging, and common operations for strings, hashes, lists, and keys.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: str | None = None,
        max_connections: int = 10,
        decode_responses: bool = True,
        logger: Logger | None = None,
    ):
        """
        Note: In async code, avoid doing network I/O (like ping) in __init__.
        Connection is verified in __aenter__ instead.
        """
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.max_connections = max_connections
        self.decode_responses = decode_responses

        self.logger = logger or getLogger(__name__)

        # Prepare pool and client (no network I/O yet)
        self.connection_pool = ConnectionPool(
            host=host,
            port=port,
            db=db,
            password=password,
            max_connections=max_connections,
            decode_responses=decode_responses,
        )
        self.redis_client = Redis(connection_pool=self.connection_pool)

    async def __aenter__(self):
        # Verify connectivity
        try:
            ok = await self.ping()
            if not ok:
                raise ConnectionError("Redis PING failed.")
            self.logger.info(
                f"Successfully connected to Redis at {self.host}:{self.port}, db: {self.db}"
            )
        except ConnectionError as e:
            self.logger.error(f"Could not connect to Redis: {e}")
            raise
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def ping(self) -> bool:
        """
        Checks the connection to Redis by pinging the server.
        """
        try:
            return await self.redis_client.ping()
        except ConnectionError:
            self.logger.error("Redis server is not available.")
            return False

    async def close(self):
        """
        Closes the client and its connection pool.
        """
        # Close the client (and pooled connections)
        try:
            await self.redis_client.close()
        except Exception as e:
            self.logger.warning(f"Error closing Redis client: {e}")

        # Explicitly disconnect the pool
        try:
            await self.connection_pool.disconnect()
        except Exception as e:
            self.logger.warning(f"Error disconnecting pool: {e}")

        self.logger.info("Redis connection pool disconnected.")

    # --- String Operations ---

    async def set_value(self, key, value, expire_seconds: int | None = None) -> bool:
        """
        Sets a string value for a given key. Dicts/lists are JSON-serialized.
        """
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            return await self.redis_client.set(key, value, ex=expire_seconds)
        except RedisError as e:
            self.logger.error(f"Error setting key '{key}': {e}")
            return False

    async def get_value(self, key):
        """
        Gets the value of a given key, JSON-deserializing when possible.

        Returns:
            - If decode_responses=True: str or dict/list or None
            - If decode_responses=False: bytes or dict/list or None
        """
        try:
            value = await self.redis_client.get(key)
            if value is None:
                return None

            # If decode_responses=True -> value is str
            if isinstance(value, str):
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value  # plain string

            # If decode_responses=False -> value is bytes
            if isinstance(value, bytes):
                try:
                    text = value.decode("utf-8")
                    return json.loads(text)
                except Exception:
                    return value  # return raw bytes if not JSON or decoding fails

            return value
        except RedisError as e:
            self.logger.error(f"Error getting key '{key}': {e}")
            return None

    # --- Hash Operations ---

    async def set_hash(self, hash_key, field, value) -> int | None:
        """
        Sets a field in a hash.
        Returns 1 if the field is new and value was set, 0 if updated, None on error.
        """
        try:
            return await self.redis_client.hset(hash_key, field, value)
        except RedisError as e:
            self.logger.error(
                f"Error setting hash field '{field}' in '{hash_key}': {e}"
            )
            return None

    async def get_hash_field(self, hash_key, field):
        """
        Gets the value of a field in a hash.
        """
        try:
            return await self.redis_client.hget(hash_key, field)
        except RedisError as e:
            self.logger.error(
                f"Error getting hash field '{field}' from '{hash_key}': {e}"
            )
            return None

    async def get_all_hash(self, hash_key) -> dict:
        """
        Gets all fields and values in a hash.
        """
        try:
            return await self.redis_client.hgetall(hash_key)
        except RedisError as e:
            self.logger.error(f"Error getting all from hash '{hash_key}': {e}")
            return {}

    # --- List Operations ---

    async def list_push(self, list_key, *values, to_right: bool = True) -> int | None:
        """
        Pushes one or more values to a list. If to_right, uses RPUSH; otherwise LPUSH.
        """
        try:
            if to_right:
                return await self.redis_client.rpush(list_key, *values)
            else:
                return await self.redis_client.lpush(list_key, *values)
        except RedisError as e:
            self.logger.error(f"Error pushing to list '{list_key}': {e}")
            return None

    async def list_pop(self, list_key, from_right: bool = True):
        """
        Pops a value from a list. If from_right, uses RPOP; otherwise LPOP.
        """
        try:
            if from_right:
                return await self.redis_client.rpop(list_key)
            else:
                return await self.redis_client.lpop(list_key)
        except RedisError as e:
            self.logger.error(f"Error popping from list '{list_key}': {e}")
            return None

    async def get_list_range(self, list_key, start: int = 0, end: int = -1) -> list:
        """
        Gets a range of elements from a list.
        """
        try:
            return await self.redis_client.lrange(list_key, start, end)
        except RedisError as e:
            self.logger.error(f"Error getting range from list '{list_key}': {e}")
            return []

    # --- Key Operations ---

    async def delete_key(self, *keys) -> int:
        """
        Deletes one or more keys. Returns the number of keys deleted.
        """
        try:
            return await self.redis_client.delete(*keys)
        except RedisError as e:
            self.logger.error(f"Error deleting keys '{keys}': {e}")
            return 0

    async def key_exists(self, key) -> bool:
        """
        Checks if a key exists.
        """
        try:
            return bool(await self.redis_client.exists(key))
        except RedisError as e:
            self.logger.error(f"Error checking existence of key '{key}': {e}")
            return False

    async def set_key_expiry(self, key, seconds: int) -> bool:
        """
        Sets an expiration time on a key.
        """
        try:
            return await self.redis_client.expire(key, seconds)
        except RedisError as e:
            self.logger.error(f"Error setting expiry for key '{key}': {e}")
            return False


# Example usage
async def main():
    try:
        # Use the class as an async context manager to ensure disconnection
        async with AsyncRedisClient(
            host="localhost",
            port=6379,
            db=0,
            password="your-very-strong-password",
            decode_responses=False,
        ) as redis_db:

            # --- String Example ---
            print("--- String Operations ---")
            user_session = {"user_id": 123, "theme": "dark"}
            await redis_db.set_value("session:123", user_session, expire_seconds=60)
            retrieved_session = await redis_db.get_value("session:123")
            print(f"Retrieved session for user 123: {retrieved_session}")
            print(f"Type of retrieved session: {type(retrieved_session)}")

            # --- Hash Example ---
            print("\n--- Hash Operations ---")
            await redis_db.set_hash("user:1000", "name", "John Doe")
            await redis_db.set_hash("user:1000", "email", "john.doe@example.com")
            user_name = await redis_db.get_hash_field("user:1000", "name")
            print(f"User 1000's name: {user_name}")
            all_user_info = await redis_db.get_all_hash("user:1000")
            print(f"All info for user 1000: {all_user_info}")

            # --- List Example (as a queue) ---
            print("\n--- List Operations (Queue) ---")
            await redis_db.list_push("task_queue", "task1", "task2", "task3")
            print(f"Current task queue: {await redis_db.get_list_range('task_queue')}")
            task = await redis_db.list_pop("task_queue", from_right=False)  # FIFO
            print(f"Processing task: {task}")
            print(f"Remaining task queue: {await redis_db.get_list_range('task_queue')}")

            # --- Key Deletion ---
            print("\n--- Key Operations ---")
            print(f"Does user:1000 exist? {await redis_db.key_exists('user:1000')}")
            await redis_db.delete_key("user:1000", "task_queue")
            print(
                f"Does user:1000 exist after deletion? {await redis_db.key_exists('user:1000')}"
            )

    except ConnectionError as e:
        print(f"Failed to connect to Redis. Please ensure the server is running. Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())