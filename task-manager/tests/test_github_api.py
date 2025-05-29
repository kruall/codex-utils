import io
import json
import unittest
from unittest.mock import patch
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from task_manager.github_api import fetch_github_tasks


class TestGitHubAPI(unittest.TestCase):
    def test_fetch_github_tasks(self) -> None:
        repo = "owner/repo"
        dir_listing = [
            {
                "name": "DEV-1.json",
                "type": "file",
                "download_url": "https://example.com/DEV-1.json",
            }
        ]
        task_data = {"id": "DEV-1", "title": "Remote task", "description": "Desc"}

        class FakeResponse(io.BytesIO):
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

        def fake_urlopen(request):
            url = request.full_url if hasattr(request, "full_url") else request.get_full_url()
            if url == f"https://api.github.com/repos/{repo}/contents/.tasks":
                return FakeResponse(json.dumps(dir_listing).encode())
            if url == dir_listing[0]["download_url"]:
                return FakeResponse(json.dumps(task_data).encode())
            raise RuntimeError("Unexpected URL")

        with patch("task_manager.github_api.urlopen", side_effect=fake_urlopen):
            tasks = fetch_github_tasks([repo])
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["id"], "DEV-1")


if __name__ == "__main__":
    unittest.main()

