from typing import Optional


def create_connection_string(
    host: str,
    port: int,
    database: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
) -> str:

    connection_string = "postgres://"

    if username:
        connection_string += username

        if password:
            connection_string += f":{password}"

        connection_string += "@"

    connection_string += f"{host}:{port}"

    if database:
        connection_string += f"/{database}"

    return connection_string
