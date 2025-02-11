def prepare_inclusion(
    default_inclusion: set[str],
    user_inclusion: set[str],
    user_exclusion: set[str],
) -> set[str]:
    if user_inclusion:
        return user_inclusion
    
    return default_inclusion - user_exclusion
