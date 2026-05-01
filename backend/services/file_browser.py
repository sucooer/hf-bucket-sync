import os
import fnmatch
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..models.schemas import FileInfo, SyncFilter


def list_directory(path: str, include_hidden: bool = False) -> list[FileInfo]:
    try:
        p = Path(path)
        if not p.exists():
            return []
        if not p.is_dir():
            return []

        files = []
        for entry in p.iterdir():
            if not include_hidden and entry.name.startswith('.'):
                continue

            stat = entry.stat()
            files.append(FileInfo(
                name=entry.name,
                path=str(entry.absolute()),
                is_dir=entry.is_dir(),
                size=stat.st_size if entry.is_file() else 0,
                modified=datetime.fromtimestamp(stat.st_mtime)
            ))

        files.sort(key=lambda x: (not x.is_dir, x.name.lower()))
        return files
    except PermissionError:
        return []
    except Exception:
        return []


def get_file_tree(path: str, max_depth: int = 3, current_depth: int = 0,
                  include_hidden: bool = False) -> list[FileInfo]:
    if current_depth >= max_depth:
        return []

    files = []
    try:
        p = Path(path)
        if not p.exists() or not p.is_dir():
            return files

        for entry in p.iterdir():
            if not include_hidden and entry.name.startswith('.'):
                continue

            stat = entry.stat()
            files.append(FileInfo(
                name=entry.name,
                path=str(entry.absolute()),
                is_dir=entry.is_dir(),
                size=stat.st_size if entry.is_file() else 0,
                modified=datetime.fromtimestamp(stat.st_mtime)
            ))

            if entry.is_dir():
                files.extend(get_file_tree(
                    str(entry.absolute()),
                    max_depth,
                    current_depth + 1,
                    include_hidden
                ))
    except PermissionError:
        pass
    except Exception:
        pass

    return files


def scan_files_with_filter(base_path: str, filter_config: SyncFilter) -> list[FileInfo]:
    all_files = get_file_tree(base_path, max_depth=100)

    filtered = []
    for f in all_files:
        if f.is_dir:
            continue

        if not _matches_filter(f.path, base_path, filter_config):
            continue

        filtered.append(f)

    return filtered


def _matches_filter(file_path: str, base_path: str, filter_config: SyncFilter) -> bool:
    rel_path = os.path.relpath(file_path, base_path)

    for pattern in filter_config.exclude_patterns:
        if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(os.path.basename(file_path), pattern):
            return False

    if filter_config.include_patterns:
        matched = False
        for pattern in filter_config.include_patterns:
            if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(os.path.basename(file_path), pattern):
                matched = True
                break
        if not matched:
            return False

    if filter_config.min_size is not None:
        size = Path(file_path).stat().st_size
        if size < filter_config.min_size:
            return False

    if filter_config.max_size is not None:
        size = Path(file_path).stat().st_size
        if size > filter_config.max_size:
            return False

    return True


def get_dir_size(path: str) -> int:
    total = 0
    try:
        for entry in Path(path).rglob('*'):
            if entry.is_file():
                total += entry.stat().st_size
    except Exception:
        pass
    return total


def format_size(size: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"