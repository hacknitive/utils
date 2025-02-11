from sys import argv

from .constant import ARGS_OF_TESTS


def is_test_mode() -> bool:
    """
        Check if the script is running in a test mode based on command-line arguments.

        This function examines the command-line arguments passed to the script and checks
        if any of the specified keywords associated with testing frameworks or test modes
        are present. It helps to determine whether the script is being executed in a test
        mode or not.

        Returns:
            bool: True if the script is running in a test mode, False otherwise.

        Raises:
            None

        Examples:
            >>> is_test_mode()
            True

        Notes:
            - The function uses the `sys.argv` list to access the command-line arguments
              passed to the script.
            - The `KEYWORDS_OF_TESTS` tuple contains the keywords or phrases that are commonly
              associated with test modes or testing frameworks. Modify this tuple to include
              additional keywords as needed for your specific use case.
            - The function performs a case-insensitive search for the keywords in the command-line
              arguments. It converts the command-line arguments to lowercase before
              performing the search.
            - If any of the specified keywords are found in the command-line arguments, the
              function returns True, indicating that the script is running in a test mode.
              Otherwise, it returns False.
        """
    args = " ".join(argv).lower()

    for i in ARGS_OF_TESTS:
        if i in args:
            return True

    return False
