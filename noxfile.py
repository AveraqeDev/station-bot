from __future__ import annotations

import typing as t
from pathlib import Path

import nox

PROJECT_DIR: t.Final = Path(__file__).parent
PROJECT_NAME: t.Final = Path(__file__).parent.stem.lower()

CHECK_PATHS: t.Final = (
    str(PROJECT_DIR / PROJECT_NAME),
    str(PROJECT_DIR / "noxfile.py"),
)


def fetch_installs(*categories: str) -> list[str]:
    installs = []

    with open(PROJECT_DIR / "requirements/dev.txt") as f:
        in_cat = None

        for line in f:
            if line.startswith("#") and line[2:].strip() in categories:
                in_cat = True
                continue

            if in_cat:
                if line == "\n":
                    in_cat = False
                    continue

                installs.append(line.strip())

    return installs


@nox.session(reuse_venv=True)
def formatting(session: nox.Session) -> None:
    session.install(*fetch_installs("Formatting"))
    session.run("black", ".", "--check")


@nox.session(reuse_venv=True)
def imports(session: nox.Session) -> None:
    session.install(*fetch_installs("Imports"))
    # flake8 doesn't use the gitignore so we have to be explicit.
    session.run(
        "flake8",
        *CHECK_PATHS,
        "--select",
        "F4",
        "--extend-ignore",
        "E,F,W",
        "--extend-exclude",
        "__init__.py",
    )
    session.run("isort", *CHECK_PATHS, "-cq")


@nox.session(reuse_venv=True)
def typing(session: nox.Session) -> None:
    session.install(*fetch_installs("Typing"), "-r", "requirements/base.txt")
    session.run("mypy", CHECK_PATHS[0])


@nox.session(reuse_venv=True)
def line_lengths(session: nox.Session) -> None:
    session.install(*fetch_installs("Line Lengths"))
    session.run("len8", *CHECK_PATHS)


@nox.session(reuse_venv=True)
def spelling(session: nox.Session) -> None:
    session.install(*fetch_installs("Spelling"))
    session.run("codespell", *CHECK_PATHS, "-L", "nd")


@nox.session(reuse_venv=True)
def safety(session: nox.Session) -> None:
    # Needed due to https://github.com/pypa/pip/pull/9827
    session.install("-U", "pip")
    session.install("-r", "requirements/dev.txt")
    session.run("safety", "check", "--full-report")


@nox.session(reuse_venv=True)
def security(session: nox.Session) -> None:
    session.install(*fetch_installs("Security"))
    session.run("bandit", "-qr", CHECK_PATHS[0], "-s", "B101")


@nox.session(reuse_venv=True)
def dependencies(session: nox.Session) -> None:
    session.install(*fetch_installs("Dependencies"))
    session.run("deputil", "update", "requirements/*.txt")
