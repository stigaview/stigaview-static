import os
import pathlib
import subprocess
import tomllib


def update_dict_list(d: dict, key: str, value: object) -> dict:
    if key not in d.keys():
        d[key] = list()
    d[key].append(value)
    return d


def get_git_revision_short_hash() -> str:
    return (
        subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
        .decode("ascii")
        .strip()
    )


def get_config() -> dict:
    config_file = pathlib.Path(
        os.environ.get("STIGAVIEW_CONFIG_FILE", "stigaview.toml")
    )
    return tomllib.loads(config_file.read_text())
