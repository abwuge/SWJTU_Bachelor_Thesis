#!/usr/bin/env python3
"""Build the thesis and install missing TeX Live packages on demand.

The package resolver prepares the primary TeX Live package list before the
official installer wrapper runs. This script is the safety net for
dependencies that are only visible while TeX expands package files, for
example a package that loads another package without declaring it in
texlive.tlpdb.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path


COMMAND_PACKAGES = {
    "biber": "biber",
    "xelatex": "xetex",
}

MISSING_FILE_PATTERNS = [
    re.compile(r"File [`'\"]([^`'\"]+)[`'\"] not found"),
    re.compile(r"! I can't find file [`'\"]?([^`'\"\s]+)"),
]


def run(command: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    print(f"+ {' '.join(command)}", flush=True)
    result = subprocess.run(
        command,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if result.stdout:
        print(result.stdout, end="")
    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, command, result.stdout)
    return result


def tlmgr(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    if shutil.which("tlmgr") is None:
        raise RuntimeError("tlmgr is not available; install TeX Live before running this script")
    return run(["tlmgr", *args], check=check)


def normalize_arch_package(package: str) -> str:
    platform = tlmgr("print-platform").stdout.strip()
    suffix = f".{platform}"
    if package.endswith(suffix):
        return package[: -len(suffix)]
    return package


def configure_tlmgr() -> None:
    tlmgr("option", "docfiles", "0")
    tlmgr("option", "srcfiles", "0")


def parse_package_from_search_output(output: str, file_name: str) -> str | None:
    current_package: str | None = None
    candidates: list[tuple[int, str]] = []

    for line in output.splitlines():
        package_match = re.match(r"^([A-Za-z0-9_.+-]+):$", line)
        if package_match:
            current_package = package_match.group(1)
            continue
        if current_package is None:
            continue
        path = line.strip()
        if not path or file_name not in path:
            continue

        if "/doc/" in path or "/source/" in path or path.startswith("doc/"):
            score = 20
        elif "/tex/" in path or path.startswith("texmf-dist/tex/"):
            score = 0
        elif path.startswith("bin/"):
            score = 1
        else:
            score = 5
        candidates.append((score, current_package))

    if not candidates:
        return None

    candidates.sort()
    return normalize_arch_package(candidates[0][1])


def package_for_file(file_name: str) -> str:
    escaped_file = re.escape(file_name)
    result = tlmgr("search", "--global", "--file", f"/{escaped_file}$", check=False)
    package = parse_package_from_search_output(result.stdout, file_name)
    if package is None:
        raise RuntimeError(f"Could not find a TeX Live package that provides {file_name}")
    return package


def install_packages(packages: set[str]) -> None:
    if not packages:
        return
    tlmgr("install", *sorted(packages))


def ensure_command(command: str) -> None:
    if shutil.which(command) is not None:
        return

    package = COMMAND_PACKAGES.get(command)
    if package is None:
        package = package_for_file(command)

    print(f"{command} is missing; installing TeX Live package {package}", flush=True)
    install_packages({package})

    if shutil.which(command) is None:
        raise RuntimeError(f"{command} is still unavailable after installing {package}")


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def find_missing_files(output: str, log_file: Path) -> set[str]:
    text = output + "\n" + read_text(log_file)
    missing: set[str] = set()
    for pattern in MISSING_FILE_PATTERNS:
        missing.update(match.group(1) for match in pattern.finditer(text))
    return {name for name in missing if not Path(name).exists()}


def latex_command(main_file: Path, build_dir: Path) -> list[str]:
    return [
        "xelatex",
        "-synctex=1",
        "-interaction=nonstopmode",
        "-file-line-error",
        f"-output-directory={build_dir}",
        str(main_file),
    ]


def build_once(main_file: Path, build_dir: Path) -> tuple[bool, set[str], int]:
    build_dir.mkdir(parents=True, exist_ok=True)
    (build_dir / "appendix").mkdir(exist_ok=True)
    (build_dir / "chapters").mkdir(exist_ok=True)

    stem = main_file.stem
    log_file = build_dir / f"{stem}.log"
    commands = [
        latex_command(main_file, build_dir),
        ["biber", f"--output-directory={build_dir}", stem],
        latex_command(main_file, build_dir),
        latex_command(main_file, build_dir),
    ]

    for command in commands:
        result = run(command, check=False)
        if result.returncode == 0:
            continue

        missing_files = find_missing_files(result.stdout, log_file)
        if missing_files:
            return False, missing_files, result.returncode
        return False, set(), result.returncode

    return True, set(), 0


def build_with_autoinstall(main_file: Path, build_dir: Path, max_rounds: int) -> int:
    configure_tlmgr()
    ensure_command("xelatex")
    ensure_command("biber")

    installed_missing_files: set[str] = set()
    for round_index in range(1, max_rounds + 1):
        print(f"Build attempt {round_index}/{max_rounds}", flush=True)
        success, missing_files, returncode = build_once(main_file, build_dir)
        if success:
            return 0

        new_missing_files = missing_files - installed_missing_files
        if not new_missing_files:
            return returncode

        package_by_file = {
            file_name: package_for_file(file_name)
            for file_name in sorted(new_missing_files)
        }
        print(
            "Installing missing TeX Live packages: "
            + ", ".join(
                f"{file_name}->{package_name}"
                for file_name, package_name in package_by_file.items()
            ),
            flush=True,
        )
        install_packages(set(package_by_file.values()))
        installed_missing_files.update(new_missing_files)

    print(f"Build did not converge after {max_rounds} attempts", file=sys.stderr)
    return 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--main", default="SWJTU_Bachelor_Thesis.tex")
    parser.add_argument("--build-dir", default="build")
    parser.add_argument("--max-rounds", type=int, default=12)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    main_file = Path(args.main)
    build_dir = Path(args.build_dir)
    return build_with_autoinstall(main_file, build_dir, args.max_rounds)


if __name__ == "__main__":
    sys.exit(main())
