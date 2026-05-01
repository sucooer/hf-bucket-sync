from fastapi import APIRouter, HTTPException, Query
import os

from ...models.schemas import BucketInfo, BucketFile
from ...services.hf_client import get_hf_client

router = APIRouter(prefix="/api/buckets", tags=["buckets"])


@router.get("")
async def list_buckets() -> list[BucketInfo]:
    try:
        client = get_hf_client()
        return client.list_buckets()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info")
async def get_bucket_info(bucket_id: str = Query(..., description="Bucket ID")) -> dict:
    try:
        client = get_hf_client()
        return client.get_bucket_info(bucket_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tree")
async def get_bucket_tree(
    bucket_id: str = Query(..., description="Bucket ID"),
    prefix: str = Query("", description="Path prefix"),
    recursive: bool = Query(True, description="Recursive listing")
) -> list[BucketFile]:
    try:
        client = get_hf_client()
        return client.list_bucket_tree(bucket_id, prefix if prefix else None, recursive)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/file")
async def delete_bucket_file(bucket_id: str = Query(...), path: str = Query(...)) -> dict:
    try:
        client = get_hf_client()
        client.delete_bucket_file(bucket_id, path)
        return {"success": True, "bucket_id": bucket_id, "path": path}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/file/rename")
async def rename_bucket_file(
    bucket_id: str = Query(...),
    old_path: str = Query(...),
    new_path: str = Query(...)
) -> dict:
    try:
        client = get_hf_client()
        client.rename_bucket_file(bucket_id, old_path, new_path)
        return {"success": True, "bucket_id": bucket_id, "old_path": old_path, "new_path": new_path}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))