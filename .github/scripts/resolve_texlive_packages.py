#!/usr/bin/env python3
"""Generate the TeX Live package list required by this repository.

The generated file is consumed by setup-texlive-action's package-file input,
so the cache key follows source-level dependency changes without maintaining
a hand-written package list.
"""

from __future__ import annotations

import argparse
import lzma
import platform
import re
import sys
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path


DEFAULT_TLPDB_URLS = [
    "https://mirrors.ctan.org/systems/texlive/tlnet/tlpkg/texlive.tlpdb.xz",
    "https://mirror.ctan.org/systems/texlive/tlnet/tlpkg/texlive.tlpdb.xz",
    "https://ctan.math.utah.edu/ctan/tex-archive/systems/texlive/tlnet/tlpkg/texlive.tlpdb.xz",
    "https://mirror.math.princeton.edu/pub/CTAN/systems/texlive/tlnet/tlpkg/texlive.tlpdb.xz",
]
BASE_PACKAGES = {
    "biber",
    "scheme-basic",
    "xetex",
}
LOCAL_PACKAGE_PREFIXES = (
    "style/",
    "./",
    "../",
)
TEXT_EXTENSIONS = {
    ".cls",
    ".ltx",
    ".sty",
    ".tex",
}


@dataclass
class TexLivePackage:
    name: str
    depends: list[str] = field(default_factory=list)
    files: list[str] = field(default_factory=list)


def guess_texlive_platform() -> str:
    machine = platform.machine().lower()
    system = platform.system().lower()
    if system == "linux" and machine in {"x86_64", "amd64"}:
        return "x86_64-linux"
    if system == "darwin":
        return "universal-darwin"
    raise RuntimeError(
        "Cannot infer TeX Live platform; pass --platform explicitly "
        "(for GitHub ubuntu-latest use x86_64-linux)"
    )


def read_tlpdb(path: Path | None, urls: list[str]) -> str:
    if path is not None:
        return lzma.decompress(path.read_bytes()).decode("utf-8", errors="replace")

    errors: list[str] = []
    for url in urls:
        try:
            print(f"Downloading TeX Live package database from {url}")
            with urllib.request.urlopen(url, timeout=45) as response:
                compressed = response.read()
            return lzma.decompress(compressed).decode("utf-8", errors="replace")
        except Exception as error:
            errors.append(f"{url}: {error}")
            print(f"Failed to download {url}: {error}", file=sys.stderr)

    raise RuntimeError(
        "Could not download texlive.tlpdb.xz from any configured URL:\n"
        + "\n".join(errors)
    )


def parse_tlpdb(text: str) -> dict[str, TexLivePackage]:
    packages: dict[str, TexLivePackage] = {}
    current: TexLivePackage | None = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if line.startswith("name "):
            current = TexLivePackage(line[5:].strip())
            packages[current.name] = current
            continue
        if current is None:
            continue
        if line.startswith("depend "):
            current.depends.append(line[7:].strip())
            continue

        file_path = line.strip()
        if re.match(r"^(RELOC|texmf-dist|bin|runfiles|srcfiles|docfiles)/", file_path):
            current.files.append(file_path.replace("RELOC/", "texmf-dist/"))

    return packages


def package_for_file(
    packages: dict[str, TexLivePackage],
    file_name: str,
    texlive_platform: str,
) -> str:
    candidates: list[tuple[int, str]] = []
    file_suffix = f"/{file_name}"

    for package in packages.values():
        for file_path in package.files:
            if not file_path.endswith(file_suffix):
                continue

            if file_path.startswith(f"bin/{texlive_platform}/"):
                score = 0
            elif file_path.startswith("texmf-dist/tex/"):
                score = 1
            elif file_path.startswith("bin/"):
                score = 8
            elif "/doc/" in file_path or "/source/" in file_path:
                score = 20
            else:
                score = 10
            candidates.append((score, package.name))

    if not candidates:
        raise RuntimeError(f"Could not find a TeX Live package providing {file_name}")

    candidates.sort()
    return candidates[0][1]


def split_tex_names(names: str) -> list[str]:
    return [name.strip() for name in names.split(",") if name.strip()]


def package_file_exists(root: Path, name: str, extension: str) -> bool:
    return (root / f"{name}{extension}").exists()


def package_is_local(root: Path, name: str, extension: str) -> bool:
    if name.startswith(LOCAL_PACKAGE_PREFIXES):
        return package_file_exists(root, name, extension)
    return package_file_exists(root, name, extension)


def collect_tex_files(root: Path) -> list[Path]:
    return [
        path
        for path in root.rglob("*")
        if path.is_file()
        and path.suffix in TEXT_EXTENSIONS
        and ".git" not in path.parts
        and "build" not in path.parts
    ]


def strip_tex_comments(text: str) -> str:
    stripped_lines: list[str] = []
    for line in text.splitlines():
        for index, character in enumerate(line):
            if character != "%":
                continue
            backslashes = 0
            cursor = index - 1
            while cursor >= 0 and line[cursor] == "\\":
                backslashes += 1
                cursor -= 1
            if backslashes % 2 == 0:
                line = line[:index]
                break
        stripped_lines.append(line)
    return "\n".join(stripped_lines)


def collect_required_files(root: Path) -> set[str]:
    required = {
        "biber",
        "xelatex",
    }

    command_pattern = re.compile(
        r"\\(?P<command>documentclass|RequirePackage|usepackage)"
        r"(?:\[(?P<options>[^\]]*)\])?"
        r"\{(?P<names>[^}]+)\}",
        re.MULTILINE,
    )
    biblatex_style_pattern = re.compile(r"style\s*=\s*([A-Za-z0-9_-]+)")

    for tex_file in collect_tex_files(root):
        text = strip_tex_comments(tex_file.read_text(encoding="utf-8", errors="replace"))
        for match in command_pattern.finditer(text):
            command = match.group("command")
            options = match.group("options") or ""
            names = split_tex_names(match.group("names"))
            if command == "documentclass":
                for name in names:
                    if not package_is_local(root, name, ".cls"):
                        required.add(f"{name}.cls")
            else:
                for name in names:
                    if not package_is_local(root, name, ".sty"):
                        required.add(f"{name}.sty")
                    if name == "biblatex":
                        for style_match in biblatex_style_pattern.finditer(options):
                            style = style_match.group(1)
                            required.add(f"{style}.bbx")
                            required.add(f"{style}.cbx")

    return required


def normalize_dependency(dependency: str, texlive_platform: str) -> str | None:
    if dependency.startswith("setting_available_architectures:"):
        return None
    if dependency.endswith(".ARCH"):
        return dependency[: -len(".ARCH")] + f".{texlive_platform}"
    return dependency


def dependency_closure(
    packages: dict[str, TexLivePackage],
    roots: set[str],
    texlive_platform: str,
) -> set[str]:
    resolved: set[str] = set()
    stack = list(roots)

    while stack:
        package_name = stack.pop()
        if package_name in resolved:
            continue
        if package_name not in packages:
            raise RuntimeError(f"Package {package_name} is not present in texlive.tlpdb")

        resolved.add(package_name)
        for dependency in packages[package_name].depends:
            normalized = normalize_dependency(dependency, texlive_platform)
            if normalized and normalized not in resolved:
                stack.append(normalized)

    return resolved


def write_package_file(path: Path, packages: set[str], required_files: set[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Generated by .github/scripts/resolve_texlive_packages.py",
        "# Do not edit by hand; update TeX sources or the resolver instead.",
        "# Runtime-only dependencies are handled by .github/scripts/build_latex.py.",
        "",
        *sorted(packages),
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")

    print(f"Resolved {len(required_files)} TeX files/commands into {len(packages)} packages")
    print(f"Wrote {path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--platform", default=None)
    parser.add_argument("--tlpdb", type=Path, default=None)
    parser.add_argument(
        "--tlpdb-url",
        action="append",
        default=[],
        help="URL for texlive.tlpdb.xz; may be passed multiple times",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    texlive_platform = args.platform or guess_texlive_platform()
    urls = args.tlpdb_url or DEFAULT_TLPDB_URLS
    packages = parse_tlpdb(read_tlpdb(args.tlpdb, urls))
    required_files = collect_required_files(root)

    root_packages = set(BASE_PACKAGES)
    for file_name in required_files:
        if file_name in {"biber", "xelatex"}:
            continue
        root_packages.add(package_for_file(packages, file_name, texlive_platform))

    resolved_packages = dependency_closure(packages, root_packages, texlive_platform)
    write_package_file(args.output, resolved_packages, required_files)
    return 0


if __name__ == "__main__":
    sys.exit(main())
