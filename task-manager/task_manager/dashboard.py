"""Generate a simple HTML dashboard from task files."""

from __future__ import annotations

from pathlib import Path
import html

from .core import TaskManager


def generate_dashboard(tasks_root: str = ".tasks", output: str = "docs/index.html") -> Path:
    """Create an HTML page listing all tasks.

    Parameters
    ----------
    tasks_root:
        Directory containing task queues.
    output:
        Path to the HTML file that will be generated.

    Returns
    -------
    Path
        Location of the generated HTML file.
    """
    tm = TaskManager(tasks_root)
    tasks = tm.task_list()

    rows = [
        "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            html.escape(task["id"]),
            html.escape(task["title"]),
            html.escape(task["status"]),
            html.escape(task["id"].rsplit("-", 1)[0]),
        )
        for task in tasks
    ]

    html_content = f"""<!DOCTYPE html>
<html lang='en'>
<head>
<meta charset='utf-8'>
<title>Task Dashboard</title>
<style>table{{border-collapse:collapse}}th,td{{border:1px solid #ccc;padding:4px}}</style>
</head>
<body>
<h1>Task Dashboard</h1>
<table>
<thead><tr><th>ID</th><th>Title</th><th>Status</th><th>Queue</th></tr></thead>
<tbody>
{'\n'.join(rows)}
</tbody>
</table>
</body>
</html>"""

    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_content, encoding="utf-8")
    return output_path
