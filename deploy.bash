#!/usr/bin/env bash
export PYTHON_VERSION=3.11
python3 -m pip install --user pipx
python3 -m pipx ensurepath
pipx install poetry
poetry install
poetry run python -m stigaview_static -o out stigs
