import glob
import subprocess

from huggingface_hub import hf_hub_download


def download_model(model_name: str, hg_user: str):
    subprocess.call("mkdir -p models", shell=True)
    if model_name not in glob.glob("models/*"):
        hf_model_path = f"{hg_user}/{model_name}"
        model_name = f"models/{model_name}"
        hf_hub_download(repo_id=hf_model_path, filename=model_name)