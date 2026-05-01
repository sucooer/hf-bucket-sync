from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import shutil

from ...models.schemas import FileInfo
from ...services.file_browser import list_directory, get_file_tree, get_dir_size, format_size

router = APIRouter(prefix="/api/files", tags=["files"])


@router.get("/list")
async def list_files(
    path: str = Query(..., description="Directory path to list"),
    include_hidden: bool = False
) -> list[FileInfo]:
    files = list_directory(path, include_hidden)
    return files


@router.get("/tree")
async def get_tree(
    path: str = Query(..., description="Base directory path"),
    max_depth: int = Query(3, ge=1, le=10),
    include_hidden: bool = False
) -> list[FileInfo]:
    files = get_file_tree(path, max_depth, 0, include_hidden)
    return files


@router.get("/size")
async def get_size(path: str = Query(..., description="Directory path")) -> dict:
    size = get_dir_size(path)
    return {
        "path": path,
        "size": size,
        "size_formatted": format_size(size)
    }


@router.get("/exists")
async def check_exists(path: str = Query(..., description="Path to check")) -> dict:
    from pathlib import Path
    p = Path(path)
    return {
        "path": path,
        "exists": p.exists(),
        "is_dir": p.is_dir() if p.exists() else False,
        "is_file": p.is_file() if p.exists() else False
    }


@router.delete("/delete")
async def delete_file(path: str = Query(..., description="Path to delete")) -> dict:
    from pathlib import Path
    p = Path(path)

    if not p.exists():
        raise HTTPException(status_code=404, detail="Path does not exist")

    try:
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()
        return {"success": True, "path": path, "deleted": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


@router.post("/rename")
async def rename_file(path: str = Query(..., description="Current path"), new_name: str = Query(..., description="New name")) -> dict:
    from pathlib import Path
    p = Path(path)

    if not p.exists():
        raise HTTPException(status_code=404, detail="Path does not exist")

    if not new_name or "/" in new_name or "\\" in new_name:
        raise HTTPException(status_code=400, detail="Invalid name")

    try:
        new_path = p.parent / new_name
        if new_path.exists():
            raise HTTPException(status_code=409, detail="Target name already exists")

        p.rename(new_path)
        return {"success": True, "old_path": path, "new_path": str(new_path)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rename failed: {str(e)}")