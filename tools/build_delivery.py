"""Build deterministic C-case delivery ZIPs and fail on version/hash drift."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path


FIXED_ZIP_TIME = (2026, 8, 8, 0, 0, 0)
FORBIDDEN_PARTS = {".env", "__pycache__", ".pytest_cache", "cookies", "cookie"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def active_versions(config_path: Path) -> dict[str, int]:
    text = config_path.read_text(encoding="utf-8")
    block = text.split("active_versions:", 1)[1]
    values: dict[str, int] = {}
    for line in block.splitlines():
        match = re.match(r"^  ([a-z]+):\s*(\d+)\s*$", line)
        if match:
            values[match.group(1)] = int(match.group(2))
        elif line and not line.startswith(" "):
            break
    return values


def safe_members(source: Path) -> list[Path]:
    members = sorted((path for path in source.rglob("*") if path.is_file()), key=lambda p: p.as_posix())
    require(members, f"empty package source: {source}")
    for path in members:
        relative = path.relative_to(source)
        lower_parts = {part.lower() for part in relative.parts}
        require(not (lower_parts & FORBIDDEN_PARTS), f"forbidden package member: {relative}")
        require(not any(part.endswith((".pyc", ".pyo")) for part in lower_parts), f"cache member: {relative}")
        require(not relative.is_absolute() and ".." not in relative.parts, f"unsafe member: {relative}")
    return members


def write_zip(source: Path, destination: Path) -> None:
    require(not destination.exists(), f"refusing to overwrite: {destination}")
    members = safe_members(source)
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in members:
            relative = path.relative_to(source).as_posix()
            info = zipfile.ZipInfo(relative, FIXED_ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compresslevel=9)


def inspect_zip(path: Path) -> dict[str, object]:
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        require(bad is None, f"corrupt ZIP member: {bad}")
        names = archive.namelist()
        require(len(names) == len(set(names)), "duplicate ZIP member")
        for name in names:
            pure = Path(name)
            require(not pure.is_absolute() and ".." not in pure.parts, f"unsafe ZIP member: {name}")
            lower = {part.lower() for part in pure.parts}
            require(not (lower & FORBIDDEN_PARTS), f"forbidden ZIP member: {name}")
            require(not name.lower().endswith((".pyc", ".pyo")), f"cache ZIP member: {name}")
    return {"file_count": len(names), "sha256": sha256(path), "members": names}


def validate_sources(case_root: Path, submission_source: Path, reproducibility_source: Path) -> dict[str, int]:
    versions = active_versions(case_root / ".mmw" / "config.yaml")
    active_code = case_root / ".mmw" / "checkpoints" / "05_code" / f"v{versions['code']}" / "solution.py"
    active_solve = case_root / ".mmw" / "checkpoints" / "06_solve" / f"v{versions['solve']}"
    active_paper = case_root / ".mmw" / "checkpoints" / "07_paper" / f"v{versions['paper']}" / "paper.pdf"
    require(sha256(submission_source / "code" / "solution.py") == sha256(active_code), "submission code drift")
    require(sha256(submission_source / "paper.pdf") == sha256(active_paper), "submission paper drift")
    require(sha256(reproducibility_source / "solution.py") == sha256(active_code), "reproducibility code drift")
    for name in ("results.json", "sensitivity.json", "method_runtime.json"):
        expected = sha256(active_solve / name)
        require(sha256(submission_source / "data" / name) == expected, f"submission {name} drift")
        require(sha256(reproducibility_source / "data" / name) == expected, f"reproducibility {name} drift")
    return versions


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("case_root", type=Path)
    parser.add_argument("submission_source", type=Path)
    parser.add_argument("reproducibility_source", type=Path)
    parser.add_argument("submission_zip", type=Path)
    parser.add_argument("reproducibility_zip", type=Path)
    args = parser.parse_args()
    case_root = args.case_root.resolve()
    versions = validate_sources(case_root, args.submission_source.resolve(), args.reproducibility_source.resolve())
    write_zip(args.submission_source.resolve(), args.submission_zip.resolve())
    write_zip(args.reproducibility_source.resolve(), args.reproducibility_zip.resolve())
    report = {
        "active_versions": versions,
        "submission": inspect_zip(args.submission_zip.resolve()),
        "reproducibility": inspect_zip(args.reproducibility_zip.resolve()),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
