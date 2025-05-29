"""Utility functions for fetching tasks from GitHub repositories."""

from __future__ import annotations

import json
from typing import List, Dict, Optional
from urllib.request import Request, urlopen
from urllib.error import URLError


GITHUB_API_BASE = "https://api.github.com/repos"


def fetch_github_tasks(repos: List[str], token: Optional[str] = None) -> List[Dict]:
    """Fetch task JSON files from given GitHub repositories.

    Parameters
    ----------
    repos:
        List of repositories in ``owner/repo`` format.
    token:
        Optional GitHub token for authenticated requests.

    Returns
    -------
    list[dict]
        Parsed task dictionaries from all repositories. Invalid files or
        network errors are ignored.
    """
    tasks: List[Dict] = []

    for repo in repos:
        contents_url = f"{GITHUB_API_BASE}/{repo}/contents/.tasks"
        req = Request(contents_url)
        if token:
            req.add_header("Authorization", f"token {token}")
        try:
            with urlopen(req) as resp:
                try:
                    dir_listing = json.load(resp)
                except json.JSONDecodeError:
                    continue
        except URLError:
            continue

        for item in dir_listing:
            if item.get("type") != "file" or not item.get("name", "").endswith(".json"):
                continue
            file_req = Request(item["download_url"])
            if token:
                file_req.add_header("Authorization", f"token {token}")
            try:
                with urlopen(file_req) as file_resp:
                    task_data = json.load(file_resp)
                tasks.append(task_data)
            except URLError:
                continue
    return tasks

