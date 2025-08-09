from redis import (
    ConnectionPool,
    Redis,
)
from redis.exceptions import (
    ConnectionError,
    RedisError,
)
import json
from logging import (
    Logger,
    getLogger,
)


class RedisClient:
    """
    A comprehensive Python class for interacting with a Redis server.

    This class uses a connection pool for efficient management of connections
    and provides methods for common Redis operations on various data types.
    It also includes error handling and logging.
    """

    def __init__(
            self,
            host: str = 'localhost',
            port: int = 6379,
            db: int = 0,
            password: str = None,
            max_connections: int = 10,
            decode_responses: bool = True,
            logger: Logger = None,
    ):
        """
        Initializes the RedisClient and sets up a connection pool.

        Args:
            host (str): The Redis server host.
            port (int): The Redis server port.
            db (int): The Redis database number.
            password (str, optional): The password for Redis authentication.
            max_connections (int): The maximum number of connections in the pool.
        """
        if logger:
            self.logger = logger
        else:
            self.logger = getLogger()

        try:
            # Create a connection pool. Using a connection pool is a best practice
            # as it saves the overhead of creating a new connection for each request. [4, 5]
            self.connection_pool = ConnectionPool(
                host=host,
                port=port,
                db=db,
                password=password,
                max_connections=max_connections,
                # Decode responses from bytes to strings [2]
                decode_responses=decode_responses,
            )
            self.redis_client = Redis(connection_pool=self.connection_pool)
            self.ping()
            self.logger.info(
                f"Successfully connected to Redis at {host}:{port}, db: {db}")
        except ConnectionError as e:
            self.logger.error(f"Could not connect to Redis: {e}")
            raise

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def ping(self):
        """
        Checks the connection to Redis by pinging the server.

        Returns:
            bool: True if the connection is alive, False otherwise.
        """
        try:
            return self.redis_client.ping()
        except ConnectionError:
            self.logger.error("Redis server is not available.")
            return False

    def close(self):
        """
        Closes the connection pool.
        """
        if self.connection_pool:
            self.connection_pool.disconnect()
            self.logger.info("Redis connection pool disconnected.")

    # --- String Operations ---

    def set_value(self, key, value, expire_seconds=None):
        """
        Sets a string value for a given key.

        Args:
            key (str): The key to set.
            value (str or dict/list): The value to store. If it's a dict or list, it will be JSON serialized.
            expire_seconds (int, optional): Time in seconds for the key to expire.

        Returns:
            bool: True if the set operation was successful, False otherwise.
        """
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            return self.redis_client.set(key, value, ex=expire_seconds)
        except RedisError as e:
            self.logger.error(f"Error setting key '{key}': {e}")
            return False

    def get_value(self, key):
        """
        Gets the value of a given key.

        Args:
            key (str): The key to retrieve.

        Returns:
            str or dict/list: The value of the key, or None if the key does not exist.
                               If the value is a JSON string, it's deserialized.
        """
        try:
            value = self.redis_client.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value  # Return as plain string if not JSON
            return None
        except RedisError as e:
            self.logger.error(f"Error getting key '{key}': {e}")
            return None

    # --- Hash Operations ---

    def set_hash(self, hash_key, field, value):
        """
        Sets a field in a hash.

        Args:
            hash_key (str): The key of the hash.
            field (str): The field within the hash to set.
            value (str): The value to set for the field.

        Returns:
            int: 1 if the field is a new field in the hash and value was set.
                 0 if the field already existed in the hash and the value was updated.
                 None on error.
        """
        try:
            return self.redis_client.hset(hash_key, field, value)
        except RedisError as e:
            self.logger.error(
                f"Error setting hash field '{field}' in '{hash_key}': {e}")
            return None

    def get_hash_field(self, hash_key, field):
        """
        Gets the value of a field in a hash.

        Args:
            hash_key (str): The key of the hash.
            field (str): The field to retrieve.

        Returns:
            str: The value of the field, or None if the field or hash does not exist.
        """
        try:
            return self.redis_client.hget(hash_key, field)
        except RedisError as e:
            self.logger.error(
                f"Error getting hash field '{field}' from '{hash_key}': {e}")
            return None

    def get_all_hash(self, hash_key):
        """
        Gets all fields and values in a hash.

        Args:
            hash_key (str): The key of the hash.

        Returns:
            dict: A dictionary of all fields and values, or an empty dict if the hash does not exist.
        """
        try:
            return self.redis_client.hgetall(hash_key)
        except RedisError as e:
            self.logger.error(f"Error getting all from hash '{hash_key}': {e}")
            return {}

    # --- List Operations ---

    def list_push(self, list_key, *values, to_right=True):
        """
        Pushes one or more values to a list.

        Args:
            list_key (str): The key of the list.
            values: The values to push to the list.
            to_right (bool): If True, pushes to the right (rpush), else to the left (lpush).

        Returns:
            int: The length of the list after the push operation, or None on error.
        """
        try:
            if to_right:
                return self.redis_client.rpush(list_key, *values)
            else:
                return self.redis_client.lpush(list_key, *values)
        except RedisError as e:
            self.logger.error(f"Error pushing to list '{list_key}': {e}")
            return None

    def list_pop(self, list_key, from_right=True):
        """
        Pops a value from a list.

        Args:
            list_key (str): The key of the list.
            from_right (bool): If True, pops from the right (rpop), else from the left (lpop).

        Returns:
            str: The popped value, or None if the list is empty or does not exist.
        """
        try:
            if from_right:
                return self.redis_client.rpop(list_key)
            else:
                return self.redis_client.lpop(list_key)
        except RedisError as e:
            self.logger.error(f"Error popping from list '{list_key}': {e}")
            return None

    def get_list_range(self, list_key, start=0, end=-1):
        """
        Gets a range of elements from a list.

        Args:
            list_key (str): The key of the list.
            start (int): The starting index.
            end (int): The ending index.

        Returns:
            list: A list of elements from the specified range.
        """
        try:
            return self.redis_client.lrange(list_key, start, end)
        except RedisError as e:
            self.logger.error(
                f"Error getting range from list '{list_key}': {e}")
            return []

    # --- Key Operations ---

    def delete_key(self, *keys):
        """
        Deletes one or more keys.

        Args:
            keys: The keys to delete.

        Returns:
            int: The number of keys that were deleted.
        """
        try:
            return self.redis_client.delete(*keys)
        except RedisError as e:
            self.logger.error(f"Error deleting keys '{keys}': {e}")
            return 0

    def key_exists(self, key):
        """
        Checks if a key exists.

        Args:
            key (str): The key to check.

        Returns:
            bool: True if the key exists, False otherwise.
        """
        try:
            return self.redis_client.exists(key)
        except RedisError as e:
            self.logger.error(f"Error checking existence of key '{key}': {e}")
            return False

    def set_key_expiry(self, key, seconds):
        """
        Sets an expiration time on a key.

        Args:
            key (str): The key to set the expiration on.
            seconds (int): The time in seconds.

        Returns:
            bool: True if the timeout was set, False otherwise.
        """
        try:
            return self.redis_client.expire(key, seconds)
        except RedisError as e:
            self.logger.error(f"Error setting expiry for key '{key}': {e}")
            return False


if __name__ == '__main__':
    try:
        # Use the class as a context manager to ensure disconnection
        with RedisClient(
            host='localhost', 
            port=6379, 
            db=0, 
            password="your-very-strong-password",
            decode_responses=False,
            ) as redis_db:

            # --- String Example ---
            print("--- String Operations ---")
            user_session = {'user_id': 123, 'theme': 'dark'}
            redis_db.set_value('session:123', user_session, expire_seconds=60)
            retrieved_session = redis_db.get_value('session:123')
            print(f"Retrieved session for user 123: {retrieved_session}")
            print(f"Type of retrieved session: {type(retrieved_session)}")

            # --- Hash Example ---
            print("\n--- Hash Operations ---")
            redis_db.set_hash('user:1000', 'name', 'John Doe')
            redis_db.set_hash('user:1000', 'email', 'john.doe@example.com')
            user_name = redis_db.get_hash_field('user:1000', 'name')
            print(f"User 1000's name: {user_name}")
            all_user_info = redis_db.get_all_hash('user:1000')
            print(f"All info for user 1000: {all_user_info}")

            # --- List Example (as a queue) ---
            print("\n--- List Operations (Queue) ---")
            redis_db.list_push('task_queue', 'task1', 'task2', 'task3')
            print(
                f"Current task queue: {redis_db.get_list_range('task_queue')}")
            task = redis_db.list_pop('task_queue', from_right=False)  # FIFO
            print(f"Processing task: {task}")
            print(
                f"Remaining task queue: {redis_db.get_list_range('task_queue')}")

            # --- Key Deletion ---
            print("\n--- Key Operations ---")
            print(f"Does user:1000 exist? {redis_db.key_exists('user:1000')}")
            redis_db.delete_key('user:1000', 'task_queue')
            print(
                f"Does user:1000 exist after deletion? {redis_db.key_exists('user:1000')}")

    except ConnectionError as e:
        print(
            f"Failed to connect to Redis. Please ensure the server is running. Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
