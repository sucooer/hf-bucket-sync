from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import shutil
import os
from pathlib import Path

from ...models.schemas import FileInfo
from ...services.file_browser import list_directory, get_file_tree, get_dir_size, format_size

router = APIRouter(prefix="/api/files", tags=["files"])

ALLOWED_BASE_DIR = Path(os.environ.get("ALLOWED_BASE_DIR", "/data")).resolve()


def _resolve_safe_path(path: str) -> Path:
    resolved = Path(path).expanduser().resolve()
    if resolved != ALLOWED_BASE_DIR and ALLOWED_BASE_DIR not in resolved.parents:
        raise HTTPException(status_code=403, detail="Path is outside allowed base directory")
    return resolved


@router.get("/list")
async def list_files(
    path: str = Query(..., description="Directory path to list"),
    include_hidden: bool = False
) -> list[FileInfo]:
    safe_path = _resolve_safe_path(path)
    files = list_directory(str(safe_path), include_hidden)
    return files


@router.get("/tree")
async def get_tree(
    path: str = Query(..., description="Base directory path"),
    max_depth: int = Query(3, ge=1, le=10),
    include_hidden: bool = False
) -> list[FileInfo]:
    safe_path = _resolve_safe_path(path)
    files = get_file_tree(str(safe_path), max_depth, 0, include_hidden)
    return files


@router.get("/size")
async def get_size(path: str = Query(..., description="Directory path")) -> dict:
    safe_path = _resolve_safe_path(path)
    size = get_dir_size(str(safe_path))
    return {
        "path": str(safe_path),
        "size": size,
        "size_formatted": format_size(size)
    }


@router.get("/exists")
async def check_exists(path: str = Query(..., description="Path to check")) -> dict:
    p = _resolve_safe_path(path)
    return {
        "path": str(p),
        "exists": p.exists(),
        "is_dir": p.is_dir() if p.exists() else False,
        "is_file": p.is_file() if p.exists() else False
    }


@router.delete("/delete")
async def delete_file(path: str = Query(..., description="Path to delete")) -> dict:
    p = _resolve_safe_path(path)

    if p == ALLOWED_BASE_DIR:
        raise HTTPException(status_code=400, detail="Deleting the base directory is not allowed")

    if not p.exists():
        raise HTTPException(status_code=404, detail="Path does not exist")

    try:
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()
        return {"success": True, "path": str(p), "deleted": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


@router.post("/rename")
async def rename_file(path: str = Query(..., description="Current path"), new_name: str = Query(..., description="New name")) -> dict:
    p = _resolve_safe_path(path)

    if not p.exists():
        raise HTTPException(status_code=404, detail="Path does not exist")

    if not new_name or "/" in new_name or "\\" in new_name:
        raise HTTPException(status_code=400, detail="Invalid name")

    try:
        new_path = (p.parent / new_name).resolve()
        if new_path != ALLOWED_BASE_DIR and ALLOWED_BASE_DIR not in new_path.parents:
            raise HTTPException(status_code=403, detail="Target path is outside allowed base directory")
        if new_path.exists():
            raise HTTPException(status_code=409, detail="Target name already exists")

        p.rename(new_path)
        return {"success": True, "old_path": path, "new_path": str(new_path)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rename failed: {str(e)}")
