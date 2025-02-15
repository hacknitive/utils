from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient
from traceback import format_exc
from logging import Logger

CODE_NAME_RUNNING_PRIORITY = (
    "collections",
    "default_documents",
    "indexes",
)

async def setup_database(
    connection_string: str,
    mqls: dict[str, dict[str, dict[str, Any]]],
    logger: Logger,
) -> None:
    try:
        print(
"""
==================================================================================
                        <<<<<< DATABASE SETUP >>>>>> 
==================================================================================
""",
        flush=True)

        client = AsyncIOMotorClient(connection_string)
        # Get the default database. You may also select a specific database if needed.
        db = client.get_default_database()

        for code_name in CODE_NAME_RUNNING_PRIORITY:
            commands = mqls.get(code_name)
            if not commands:
                logger.info("This code is empty: %s", code_name)
                continue

            db.create_collection(collection_name, validator=schema)

            logger.info("Command to execute: %s", compiled_commands)
            
            # Example (if you had a valid command dictionary):
            # result = await db.command(your_command_dict)
            #
            # Alternatively, if you must evaluate a script, you might be tempted to do:
            # result = await db.command({"eval": compiled_commands})
            # However, the eval command is deprecated for security reasons.

    except Exception:
        logger.critical(format_exc())
        raise

    finally:
        try:
            client.close()  # Synchronously close the Motor client.
            logger.info("MongoDB client is closed.")
        except Exception:
            pass