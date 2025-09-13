from typing import Callable
from secrets import compare_digest

from fastapi import (
    Depends,
    status,
)
from fastapi.security import (
    HTTPBasic,
    HTTPBasicCredentials,
)

from ...exception import ProjectBaseException

security = HTTPBasic()


def add_http_basic_security_builder(
        user_name: str,
        password: str,
 ) -> Callable:

    def add_http_basic_security(
        credentials: HTTPBasicCredentials = Depends(security),
    ) -> None:
        correct_username = compare_digest(
            credentials.username,
            user_name
        )
        correct_password = compare_digest(
            credentials.password,
            password
        )
        if not (
            correct_username
            and
            correct_password
        ):
            raise ProjectBaseException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="Incorrect username or password",
                headers={"WWW-Authenticate": "Basic"},
                data=None,
                success=False
            )
        return None
    
    return add_http_basic_security
