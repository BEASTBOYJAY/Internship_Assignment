import os
from huggingface_hub import snapshot_download as hf_snapshot_download

from miner_u_parser.utils.enum_class import ModelPath


def auto_download_and_get_model_root_path(relative_path: str) -> str:
    """
    Reliably downloads files or directories from Hugging Face for the pipeline.
    - If input is a file: returns the absolute path to the local file.
    - If input is a directory: returns the path to the directory in the local cache.
    :param relative_path: The relative path of the file or directory in the repository.
    :return: The absolute path to the cached model/file.
    """
    repo = ModelPath.pipeline_root_hf

    snapshot_download = hf_snapshot_download

    relative_path = relative_path.strip("/")
    cache_dir = snapshot_download(
        repo, allow_patterns=[relative_path, relative_path + "/*"]
    )

    if not cache_dir:
        raise FileNotFoundError(
            f"Failed to download model: {relative_path} from {repo}"
        )

    return cache_dir
