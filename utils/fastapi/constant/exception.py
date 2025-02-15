from utils.exception import ProjectBaseException

from .status_code import *
from .message import *

EXCEPTION_SERVER_ERROR = ProjectBaseException(
    status_code=HTTP_500_INTERNAL_SERVER_ERROR,
    success=False,
    data=None,
    error=MESSAGE_SERVER_ERROR,
    message=MESSAGE_SERVER_ERROR,
)

EXCEPTION_UNAUTHENTICATED_USER = ProjectBaseException(
    status_code=HTTP_401_UNAUTHORIZED,
    success=False,
    data=None,
    error=MESSAGE_UNAUTHENTICATED_USER,
    message=MESSAGE_UNAUTHENTICATED_USER,
)

EXCEPTION_UNAUTHORIZED_USER = ProjectBaseException(
    status_code=HTTP_403_FORBIDDEN,
    success=False,
    data=None,
    error=MESSAGE_UNAUTHORIZED_USER,
    message=MESSAGE_UNAUTHORIZED_USER,
)