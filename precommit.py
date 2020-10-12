#!/usr/bin/env python3
"""Run precommit checks on the repository."""
import argparse
import os
import pathlib
import re
import subprocess
import sys


def main() -> int:
    """Execute the main routine."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--overwrite",
        help="Overwrites the unformatted source files with the "
        "well-formatted code in place. If not set, "
        "an exception is raised if any of the files do not conform "
        "to the style guide.",
        action='store_true')

    args = parser.parse_args()

    overwrite = bool(args.overwrite)

    repo_root = pathlib.Path(__file__).parent

    # yapf: disable
    source_files = (
                sorted((repo_root / "datetime_glob").glob("**/*.py")) +
                sorted((repo_root / "tests").glob("**/*.py")))
    # yapf: enable

    if overwrite:
        print('Removing trailing whitespace...')
        for pth in source_files:
            pth.write_text(re.sub(r'[ \t]+$', '', pth.read_text(), flags=re.MULTILINE))

    print("YAPF'ing...")
    yapf_targets = ["tests", "datetime_glob", "setup.py", "precommit.py"]
    if overwrite:
        # yapf: disable
        subprocess.check_call(
            ["yapf", "--in-place", "--style=style.yapf", "--recursive"] +
            yapf_targets,
            cwd=str(repo_root))
        # yapf: enable
    else:
        # yapf: disable
        subprocess.check_call(
            ["yapf", "--diff", "--style=style.yapf", "--recursive"] +
            yapf_targets,
            cwd=str(repo_root))
        # yapf: enable

    print("Mypy'ing...")
    subprocess.check_call(["mypy", "--strict", "datetime_glob", "tests"], cwd=str(repo_root))

    print("Isort'ing...")
    # yapf: disable
    isort_files = map(str, source_files)
    # yapf: enable

    if overwrite:
        cmd = ["isort", "--project", "datetime_glob"]
        cmd.extend(str(pth) for pth in source_files)

        subprocess.check_call(cmd)
    else:
        cmd = ["isort", "--check-only", "--project", "datetime_glob"]
        cmd.extend(str(pth) for pth in source_files)
        subprocess.check_call(cmd)

    print("Pydocstyle'ing...")
    subprocess.check_call(["pydocstyle", "datetime_glob"], cwd=str(repo_root))

    print("Pylint'ing...")
    subprocess.check_call(["pylint", "--rcfile=pylint.rc", "tests", "datetime_glob"], cwd=str(repo_root))

    print("Testing...")
    env = os.environ.copy()
    env['ICONTRACT_SLOW'] = 'true'

    # yapf: disable
    subprocess.check_call(
        ["coverage", "run",
         "--source", "datetime_glob",
         "-m", "unittest", "discover", "tests"],
        cwd=str(repo_root),
        env=env)
    # yapf: enable

    subprocess.check_call(["coverage", "report"])

    print("Doctesting...")
    doctest_files = ([repo_root / "README.rst"] + sorted((repo_root / "datetime_glob").glob("**/*.py")))

    for pth in doctest_files:
        subprocess.check_call([sys.executable, "-m", "doctest", str(pth)])

    print("Checking setup.py sdist ...")
    subprocess.check_call([sys.executable, "setup.py", "sdist"], cwd=str(repo_root))

    print("Checking with twine...")
    subprocess.check_call(["twine", "check", "dist/*"], cwd=str(repo_root))

    return 0


if __name__ == "__main__":
    sys.exit(main())
