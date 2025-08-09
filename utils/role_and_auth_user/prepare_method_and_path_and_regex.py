from re import compile

PLACEHOLDER_RE = compile(r'{[^/]+}')

def convert_pattern_to_regex(route_pattern: str) -> str:
    regex = PLACEHOLDER_RE.sub(r'([^/]+)', route_pattern)
    return f"^{regex}$"


def prepare_method_and_path_and_regex(method_path: str):
    method, path = method_path.split(":", maxsplit=1)
    return {
        "method": method.upper(),
        "path": path,
        "regex": convert_pattern_to_regex(route_pattern=path)
    }