#!/usr/bin/env python3
"""Install TeX Live with the official installer and a generated package list."""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path


DEFAULT_INSTALLER_URL = "https://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz"
DEFAULT_REPOSITORY = "https://mirror.ctan.org/systems/texlive/tlnet"
DEFAULT_FALLBACK_REPOSITORIES = [
    "https://latex.us/systems/texlive/tlnet",
    "https://ctan.math.utah.edu/ctan/tex-archive/systems/texlive/tlnet",
    "https://mirror.math.princeton.edu/pub/CTAN/systems/texlive/tlnet",
]
DEFAULT_TEXLIVE_ROOT = Path(".texlive")


def run(command: list[str], *, env: dict[str, str] | None = None) -> None:
    print(f"+ {' '.join(command)}", flush=True)
    subprocess.run(command, check=True, env=env)


def run_with_output(
    command: list[str],
    *,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    print(f"+ {' '.join(command)}", flush=True)
    result = subprocess.run(
        command,
        check=False,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if result.stdout:
        print(result.stdout, end="")
    return result


def read_package_file(path: Path) -> tuple[list[str], str | None]:
    packages: list[str] = []
    release: str | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("# TeX Live release:"):
            value = line.removeprefix("# TeX Live release:").strip()
            if value != "unknown":
                release = value
            continue
        if line and not line.startswith("#"):
            packages.append(line)
    return packages, release


def append_github_path(path: Path) -> None:
    github_path = os.environ.get("GITHUB_PATH")
    if github_path is None:
        return
    with Path(github_path).open("a", encoding="utf-8") as output:
        print(path, file=output)


def bin_dir(texlive_dir: Path, platform: str) -> Path:
    return texlive_dir / "bin" / platform


def guess_texlive_platform() -> str:
    machine = platform.machine().lower()
    system = platform.system().lower()
    if system == "linux" and machine in {"x86_64", "amd64"}:
        return "x86_64-linux"
    if system == "darwin":
        return "universal-darwin"
    raise RuntimeError("Cannot infer TeX Live platform; pass --platform explicitly")


def find_installer(root: Path) -> Path:
    candidates = sorted(root.glob("install-tl-*/install-tl"))
    if not candidates:
        raise RuntimeError("Could not find install-tl in the downloaded archive")
    return candidates[0]


def download_installer(url: str, output: Path) -> None:
    print(f"Downloading TeX Live installer from {url}", flush=True)
    with urllib.request.urlopen(url, timeout=120) as response:
        output.write_bytes(response.read())


def ensure_within_directory(root: Path, path: Path) -> None:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError as error:
        raise RuntimeError(f"Archive member escapes extraction directory: {path}") from error


def extract_installer(archive: Path, destination: Path) -> None:
    with tarfile.open(archive, "r:gz") as tar:
        for member in tar.getmembers():
            member_path = destination / member.name
            ensure_within_directory(destination, member_path)
            if member.issym() or member.islnk():
                link_target = Path(member.linkname)
                if link_target.is_absolute():
                    raise RuntimeError(f"Archive member has absolute link target: {member.name}")
                ensure_within_directory(destination, member_path.parent / link_target)
        if sys.version_info >= (3, 12):
            tar.extractall(destination, filter="data")
        else:
            tar.extractall(destination)


def install_infra(
    texlive_dir: Path,
    repository: str,
    installer_url: str,
    platform: str,
) -> None:
    tlmgr = bin_dir(texlive_dir, platform) / "tlmgr"
    if tlmgr.exists():
        print(f"Found cached TeX Live installation at {texlive_dir}", flush=True)
        return

    if texlive_dir.exists():
        shutil.rmtree(texlive_dir)
    texlive_dir.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="install-tl-") as temp_name:
        temp_dir = Path(temp_name)
        archive = temp_dir / "install-tl-unx.tar.gz"
        download_installer(installer_url, archive)
        extract_installer(archive, temp_dir)

        installer = find_installer(temp_dir)
        run(
            [
                str(installer),
                "--no-interaction",
                "--scheme",
                "scheme-infraonly",
                "--no-doc-install",
                "--no-src-install",
                "--repository",
                repository,
                "--force-platform",
                platform,
                "--texdir",
                str(texlive_dir),
            ]
        )


def package_install_is_retryable(output: str) -> bool:
    return "seems to be older than the local installation" in output


def install_packages(
    tlmgr: str,
    packages: list[str],
    fallback_repositories: list[str],
    *,
    env: dict[str, str],
) -> None:
    install_command = [tlmgr, "install", *packages]
    result = run_with_output(install_command, env=env)
    if result.returncode == 0:
        return

    if not package_install_is_retryable(result.stdout):
        raise subprocess.CalledProcessError(result.returncode, install_command, result.stdout)

    for repository in fallback_repositories:
        print(f"Retrying TeX Live package install with {repository}", flush=True)
        run([tlmgr, "option", "repository", repository], env=env)
        result = run_with_output(install_command, env=env)
        if result.returncode == 0:
            return
        if not package_install_is_retryable(result.stdout):
            raise subprocess.CalledProcessError(result.returncode, install_command, result.stdout)

    raise subprocess.CalledProcessError(result.returncode, install_command, result.stdout)


def setup_texlive(args: argparse.Namespace) -> None:
    packages, release = read_package_file(args.package_file)
    if not packages:
        raise RuntimeError(f"No packages found in {args.package_file}")
    platform_name = args.platform or guess_texlive_platform()
    texlive_dir = (args.texlive_dir or (args.texlive_root / (release or "current"))).resolve()

    install_infra(texlive_dir, args.repository, args.installer_url, platform_name)

    texlive_bin = bin_dir(texlive_dir, platform_name)
    if not texlive_bin.exists():
        raise RuntimeError(f"TeX Live bin directory does not exist: {texlive_bin}")

    env = os.environ.copy()
    env["PATH"] = f"{texlive_bin}{os.pathsep}{env.get('PATH', '')}"

    tlmgr = str(texlive_bin / "tlmgr")
    run([tlmgr, "option", "docfiles", "0"], env=env)
    run([tlmgr, "option", "srcfiles", "0"], env=env)
    install_packages(tlmgr, packages, args.fallback_repository, env=env)
    append_github_path(texlive_bin)

    print(f"TeX Live is ready at {texlive_dir}", flush=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-file", type=Path, required=True)
    parser.add_argument("--texlive-root", type=Path, default=DEFAULT_TEXLIVE_ROOT)
    parser.add_argument("--texlive-dir", type=Path, default=None)
    parser.add_argument("--platform", default=None)
    parser.add_argument("--installer-url", default=DEFAULT_INSTALLER_URL)
    parser.add_argument("--repository", default=DEFAULT_REPOSITORY)
    parser.add_argument(
        "--fallback-repository",
        action="append",
        default=DEFAULT_FALLBACK_REPOSITORIES,
    )
    return parser.parse_args()


def main() -> int:
    try:
        setup_texlive(parse_args())
    except Exception as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
