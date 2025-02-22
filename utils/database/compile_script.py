from pathlib import Path


def compile_script(
        this_file_path: Path | str,
        compiled_scripts: dict[str, list],
        extension_pattern: str = "*.sql",
        script_directory_name: str = "sql",
        comment_start_with: str = "--"
) -> None:

    directory = Path(this_file_path).resolve(
        ).parents[0] / script_directory_name

    files: list[Path] = list(directory.glob(extension_pattern))

    for file in files:
        with open(file, "r", encoding="utf-8") as handler:
            content_lines = handler.readlines()

        cleaned_content = list()
        for content_line in content_lines: 
            if not content_line.startswith(comment_start_with):
                if content_line.endswith("\n"):
                    content_line = content_line[:-1]

                if content_line:
                    cleaned_content.append(content_line)

        cleaned_content_compiled = "\n".join(cleaned_content)
        if cleaned_content_compiled:
            if file.stem in compiled_scripts:
                compiled_scripts[file.stem].append(cleaned_content_compiled)
            else:
                compiled_scripts[file.stem] = [cleaned_content_compiled]

    return None
