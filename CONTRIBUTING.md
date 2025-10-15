# STIG A View Static Contributors Guide

Thanks for your interest in contributing to STIG A View.
This document has a few notes that should help you with contributing.


## Development Environment setup
Requirements
* Python 3.11+
* Python venv module
* Make
* GNU Sed

### Fedora

```bash
sudo dnf install python3 make sed
```

### Debian/Ubuntu
```bash
sudo apt install python3 python3-venv make sed
```

### macOS
GNU Sed is needed for sitemaps generation.
```bash
brew install gnu-sed make
```

Create a virtual environment (venv), activate the venv, and install the Python dependencies.

```
$ python -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```

To build the site run:
```
$ make
```

### Windows
Native Windows development isn't fully supported.
It is sugguested that you use [Windows Subsystem for Linux](https://learn.microsoft.com/en-us/windows/wsl/install) (WSL).
Setting that up is out-of-scope for this document.

However, you can follow the steps above to install Python dependencies (assume you have working Python installation on Windows) then run the cli using `python -m stigaview`.

Pre-commit also runs in CI so you can use those results if don't want to install the pre-commit hooks.

Install the pre-commit hooks if so desired by running the following command:

```bash
pre-commit install
```

## Make a Contribution
1. [Fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo) [this repo](https://github.com/stigaview/stigaview-static)
2. Create a branch
   1. `git checkout -b my_cool_feature`
3. Do your changes
4. Format your code
   1. This project uses the [black formatter](https://black.readthedocs.io/en/stable/). Please use pre-commit or run black on your own.
5. Commit your changes
   1. Please follow [How to Write a Git Commit Message](https://cbea.ms/git-commit/) by [cbeams](https://cbea.ms/) when writing commit messages
   2. All commits must be GPG signed. GitHub as a [good guide](https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-commits) on how to set this up.
   3. Please sign off (using `-s or `--sign-off`)
6. Open a pull reqeust on [the repo](https://github.com/stigaview/stigaview-static)
