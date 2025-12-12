#!/usr/bin/env python3
import os
import sys
import shutil
from pathlib import Path
import requests
import tempfile
import tarfile
import zipfile

try:
    from huggingface_hub import snapshot_download
except Exception:
    snapshot_download = None


def download_from_url(url: str, dest: Path):
    dest.mkdir(parents=True, exist_ok=True)
    print(f"Downloading model archive from: {url}")
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    tmp.write(chunk)
            tmp_path = Path(tmp.name)

    # try to extract if it's an archive
    try:
        if zipfile.is_zipfile(tmp_path):
            with zipfile.ZipFile(tmp_path, 'r') as z:
                z.extractall(dest)
        elif tarfile.is_tarfile(tmp_path):
            with tarfile.open(tmp_path, 'r:*') as t:
                t.extractall(dest)
        else:
            # Not an archive: treat as single file
            target_file = dest / tmp_path.name
            shutil.move(str(tmp_path), str(target_file))
            print(f"Saved file to {target_file}")
            return
    finally:
        try:
            if tmp_path.exists():
                tmp_path.unlink()
        except Exception:
            pass


def download_from_hf(repo_id: str, dest: Path, token: str | None = None):
    if snapshot_download is None:
        raise RuntimeError("huggingface_hub not available in the environment")
    print(f"Downloading model from Hugging Face hub: {repo_id}")
    # snapshot_download returns path to cache directory containing model files
    kwargs = {}
    if token:
        kwargs["use_auth_token"] = token
    cache_path = snapshot_download(repo_id, **kwargs)
    # copy contents from cache_path to dest
    dest.mkdir(parents=True, exist_ok=True)
    for item in Path(cache_path).iterdir():
        target = dest / item.name
        if item.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)


def main():
    target = Path("/app/Model")

    # If already exists and not empty, skip
    if target.exists() and any(target.iterdir()):
        print("Model directory already exists and is not empty — skipping download.")
        return 0

    hf_repo = os.environ.get("MODEL_HF_ID")
    hf_token = os.environ.get("HF_HUB_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")
    model_url = os.environ.get("MODEL_URL")

    if hf_repo:
        try:
            download_from_hf(hf_repo, target, hf_token)
            print("Downloaded model from Hugging Face Hub.")
            return 0
        except Exception as e:
            print(f"Failed to download from Hugging Face: {e}")

    if model_url:
        try:
            download_from_url(model_url, target)
            print("Downloaded model from URL.")
            return 0
        except Exception as e:
            print(f"Failed to download from URL: {e}")

    print("No model source provided. Set MODEL_HF_ID or MODEL_URL environment variable.")
    return 2


if __name__ == "__main__":
    sys.exit(main())
