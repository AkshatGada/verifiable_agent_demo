import os
import requests
import hashlib

def fetch_readme(repo_url: str) -> tuple[str, str]:
    owner, name = repo_url.rstrip("/").split("/")[-2:]
    api = f"https://api.github.com/repos/{owner}/{name}/readme"
    headers = {"Accept": "application/vnd.github.raw"}
    if tok := os.getenv("GH_TOKEN"):
        headers["Authorization"] = f"token {tok}"
    res = requests.get(api, headers=headers, timeout=20)
    res.raise_for_status()
    return f"{owner}/{name}", res.text


def fetch_and_hash(repo_url: str):
    """
    Returns: (repo_name, readme_text, sha256_digest_hex)
    """
    owner, name = repo_url.rstrip("/").split("/")[-2:]
    api = f"https://api.github.com/repos/{owner}/{name}/readme"
    headers = {"Accept": "application/vnd.github.raw"}
    if tok := os.getenv("GH_TOKEN"):
        headers["Authorization"] = f"token {tok}"
    res = requests.get(api, headers=headers, timeout=20)
    res.raise_for_status()
    text   = res.text
    digest = hashlib.sha256(text.encode()).hexdigest()
    return f"{owner}/{name}", text, digest