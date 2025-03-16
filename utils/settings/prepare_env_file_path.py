from os import environ
from pathlib import Path

from dotenv import load_dotenv


def prepare_env_file_path(base_dir_path: Path,) -> None | Path:
    env_file_name = environ.get("ENV_FILE_NAME")

    if env_file_name:
        env_file_path = base_dir_path / env_file_name

        load_dotenv(  # Sometimes python caches the .env, especially in vscode
            dotenv_path=env_file_path,
            override=True,
        )
    else:
        print("!!!!!! no .env file found!")
        env_file_path = None

    return env_file_path

