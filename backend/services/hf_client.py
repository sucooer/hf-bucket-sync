import os
import io
from typing import Optional

from huggingface_hub import HfApi, list_buckets, bucket_info, list_bucket_tree
from huggingface_hub import sync_bucket as hf_sync_bucket


class HFClient:
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.environ.get("HF_TOKEN")
        if not self.token:
            raise ValueError("HF_TOKEN is required. Set environment variable or pass token.")
        self.api = HfApi(token=self.token)

    def list_buckets(self):
        buckets = list_buckets()
        return [
            {
                "id": b.id,
                "private": b.private,
                "size": b.size,
                "total_files": b.total_files
            }
            for b in buckets
        ]

    def get_bucket_info(self, bucket_id: str) -> dict:
        info = bucket_info(bucket_id)
        return {
            "id": info.id,
            "private": info.private,
            "size": info.size,
            "total_files": info.total_files,
            "created_at": info.created_at.isoformat() if info.created_at else None
        }

    def list_bucket_tree(self, bucket_id: str, prefix: Optional[str] = None, recursive: bool = True):
        items = list_bucket_tree(bucket_id, prefix=prefix, recursive=recursive)
        return [
            {
                "path": item.path,
                "type": item.type,
                "size": getattr(item, 'size', 0)
            }
            for item in items
        ]

    def delete_bucket_file(self, bucket_id: str, path: str):
        self.api.batch_bucket_files(bucket_id, delete=[path])

    def rename_bucket_file(self, bucket_id: str, old_path: str, new_path: str):
        import tempfile
        import os
        import shutil

        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.basename(old_path)
            local_file = os.path.join(tmpdir, filename)

            hf_sync_bucket(
                source=f"hf://buckets/{bucket_id}/{old_path}".rstrip("/"),
                dest=tmpdir,
                delete=False,
                dry_run=False,
                verbose=False
            )

            if os.path.exists(local_file):
                new_dir = os.path.join(tmpdir, "new")
                os.makedirs(new_dir, exist_ok=True)
                new_local = os.path.join(new_dir, os.path.basename(new_path))
                shutil.move(local_file, new_local)

                parent_path = os.path.dirname(new_path)
                dest_path = f"hf://buckets/{bucket_id}/{parent_path}".rstrip("/") if parent_path else f"hf://buckets/{bucket_id}"

                hf_sync_bucket(
                    source=new_dir,
                    dest=dest_path,
                    delete=False,
                    dry_run=False,
                    verbose=False
                )

                self.delete_bucket_file(bucket_id, old_path)

    def sync_bucket(self, local_path: str, bucket_path: str, direction: str = "upload",
                    delete: bool = False, include: Optional[list] = None,
                    exclude: Optional[list] = None, dry_run: bool = False,
                    verbose: bool = True):
        if direction == "upload":
            source = local_path
            destination = f"hf://buckets/{bucket_path}"
        else:
            source = f"hf://buckets/{bucket_path}"
            destination = local_path

        return hf_sync_bucket(
            source,
            destination,
            delete=delete,
            include=include,
            exclude=exclude,
            dry_run=dry_run,
            verbose=verbose
        )


_client: Optional[HFClient] = None


def get_hf_client() -> HFClient:
    global _client
    if _client is None:
        _client = HFClient()
    return _client


def reset_hf_client():
    global _client
    _client = None