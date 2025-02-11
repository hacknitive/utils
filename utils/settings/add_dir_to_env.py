from sys import path
from os import environ, pathsep


def add_dir_to_env(path_: str) -> str:
    """
    Add a directory path to the Python runtime environment.

    This function takes a directory path as input and adds it to the Python
    runtime environment. It modifies both the 'sys.path' list and the 'PYTHONPATH'
    environment variable to include the specified directory.

    Args:
        path_ (str): The directory path to be added to the Python environment.

    Returns:
        str: The updated directory path that has been added to the Python environment.

    Raises:
        None

    Examples:
        >>> add_dir_to_env('/path/to/mydir')
        '/path/to/mydir'

    Notes:
        - If the specified directory path is already present in 'sys.path', it will not
          be added again.
        - If the 'PYTHONPATH' environment variable is not set, it will be initialized as
          an empty string before adding the directory path.
        - The 'PYTHONPATH' environment variable is a string containing a list of directory
          paths separated by the platform-specific path separator character (e.g., ':' on
          Unix-like systems and ';' on Windows).

    """
    if path_ not in path:
        path.append(path_)

    if "PYTHONPATH" not in environ:
        environ["PYTHONPATH"] = ''

    environ["PYTHONPATH"] += pathsep + path_

    return path_
