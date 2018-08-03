#!/usr/bin/env python3
"""
Runs precommit checks on the repository.
"""
import argparse
import concurrent.futures
import hashlib
import pathlib
import subprocess
import sys
from typing import List, Union, Tuple  # pylint: disable=unused-import

import yapf.yapflib.yapf_api


def compute_hash(text: str) -> str:
    """
    :param text: to hash
    :return: hash digest
    """
    md5 = hashlib.md5()
    md5.update(text.encode())
    return md5.hexdigest()


class Hasher:
    """
    Hashes the source code files and reports if they differed to one of the previous hashings.
    """

    def __init__(self, source_dir: pathlib.Path, hash_dir: pathlib.Path) -> None:
        self.source_dir = source_dir
        self.hash_dir = hash_dir

    def __hash_dir(self, path: pathlib.Path) -> pathlib.Path:
        """
        :param path: to a source file
        :return: path to the file holding the hash of the source text
        """
        if self.source_dir not in path.parents:
            raise ValueError("Expected the path to be beneath the source directory {!r}, got: {!r}".format(
                str(self.source_dir), str(path)))

        return self.hash_dir / path.relative_to(self.source_dir).parent / path.name

    def hash_differs(self, path: pathlib.Path) -> bool:
        """
        :param path: to the source file
        :return: True if the hash of the content differs to the previous hashing.
        """
        hash_dir = self.__hash_dir(path=path)

        if not hash_dir.exists():
            return True

        prev_hashes = set([pth.name for pth in hash_dir.iterdir()])

        new_hsh = compute_hash(text=path.read_text())

        return not new_hsh in prev_hashes

    def update_hash(self, path: pathlib.Path) -> None:
        """
        Hashes the file content and stores it on disk.

        :param path: to the source file
        :return:
        """
        hash_dir = self.__hash_dir(path=path)
        hash_dir.mkdir(exist_ok=True, parents=True)

        new_hsh = compute_hash(text=path.read_text())

        pth = hash_dir / new_hsh
        pth.write_text('passed')


def check(path: pathlib.Path, py_dir: pathlib.Path, force: bool) -> Union[None, str]:
    """
    Runs all the checks on the given file.

    :param path: to the source file
    :param py_dir: path to the source files
    :param force: if True, overwrites the source file in place instead of reporting that it was not well-formatted.
    :return: None if all checks passed. Otherwise, an error message.
    """
    style_config = py_dir / 'style.yapf'

    report = []

    # yapf
    if not force:
        formatted, _, changed = yapf.yapflib.yapf_api.FormatFile(
            filename=str(path), style_config=str(style_config), print_diff=True)

        if changed:
            report.append("Failed to yapf {}:\n{}".format(path, formatted))
    else:
        yapf.yapflib.yapf_api.FormatFile(filename=str(path), style_config=str(style_config), in_place=True)

    # mypy
    proc = subprocess.Popen(
        ['mypy', str(path), '--ignore-missing-imports'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True)
    stdout, stderr = proc.communicate()
    if proc.returncode != 0:
        report.append("Failed to mypy {}:\nOutput:\n{}\n\nError:\n{}".format(path, stdout, stderr))

    # pylint
    proc = subprocess.Popen(
        ['pylint', str(path), '--rcfile={}'.format(py_dir / 'pylint.rc')],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True)

    stdout, stderr = proc.communicate()
    if proc.returncode != 0:
        report.append("Failed to pylint {}:\nOutput:\n{}\n\nError:\n{}".format(path, stdout, stderr))

    if len(report) > 0:
        return "\n".join(report)

    return None


def main() -> int:
    """"
    Main routine
    """
    # pylint: disable=too-many-locals
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--force",
        help="Overwrites the unformatted source files with the well-formatted code in place. "
        "If not set, an exception is raised if any of the files do not conform to the style guide.",
        action='store_true')
    args = parser.parse_args()

    force = args.force
    assert isinstance(force, bool)

    py_dir = pathlib.Path(__file__).parent

    hash_dir = py_dir / '.precommit_hashes'
    hash_dir.mkdir(exist_ok=True)

    hasher = Hasher(source_dir=py_dir, hash_dir=hash_dir)

    # yapf: disable
    pths = sorted(
        list(py_dir.glob("*.py")) +
        list((py_dir / 'datetime_glob').glob("*.py")) +
        list((py_dir / 'tests').glob("*.py"))
    )
    # yapf: enable

    # see which files changed:
    changed_pths = []  # type: List[pathlib.Path]
    for pth in pths:
        if hasher.hash_differs(path=pth):
            changed_pths.append(pth)

    if len(changed_pths) == 0:
        print("No file changed since the last pre-commit check.")
        return 0

    print("There are {} file(s) that need to be checked...".format(len(changed_pths)))

    success = True

    futures_paths = []  # type: List[Tuple[concurrent.futures.Future, pathlib.Path]]
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for pth in changed_pths:
            future = executor.submit(fn=check, path=pth, py_dir=py_dir, force=force)
            futures_paths.append((future, pth))

        for future, pth in futures_paths:
            report = future.result()
            if report is None:
                print("Passed all checks: {}".format(pth))
                hasher.update_hash(path=pth)
            else:
                print("One or more checks failed for {}:\n{}".format(pth, report))
                success = False

    print("Running unit tests...")
    source_dir = pathlib.Path(__file__).resolve().parent
    retcode = subprocess.call(['python3', '-m', 'unittest', 'discover', str(source_dir / 'tests')])
    success = success and retcode == 0

    if not success:
        print("One or more checks failed.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
