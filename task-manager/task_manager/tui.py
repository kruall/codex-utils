import logging
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .core import TaskManager

def launch_tui(tm: "TaskManager") -> None:
    """Launch the Textual TUI for the task manager."""
    if TYPE_CHECKING:  # pragma: no cover - type hints only
        from textual.app import App, ComposeResult  # type: ignore
        from textual.widgets import Header, Footer, Button, Static, Input, DataTable  # type: ignore
        from textual.containers import Vertical  # type: ignore

    try:
        from textual.app import App, ComposeResult  # type: ignore
        from textual.widgets import Header, Footer, Button, Static, Input, DataTable  # type: ignore
        from textual.containers import Vertical  # type: ignore
    except Exception:  # pragma: no cover - optional dependency
        logging.getLogger(__name__).error(
            "Textual is required for the UI. Install with 'pip install textual'"
        )
        return

    class TMApp(App):
        TITLE = "Task Manager"
        BINDINGS = [("q", "quit", "Quit")]

        def __init__(self, manager: "TaskManager") -> None:
            super().__init__()
            self.manager = manager
            self.body: Vertical | None = None
            self.current_task_id: str | None = None

        def compose(self) -> ComposeResult:
            yield Header(show_clock=True)
            yield Footer()
            self.body = Vertical()
            yield self.body

        def on_mount(self) -> None:
            """Called when the app is mounted and ready."""
            self.show_main()

        def show_main(self) -> None:
            assert self.body
            self.body.remove_children()
            self.body.mount(Static("Task Manager", classes="title"))
            self.body.mount(Button("Queues", id="queues"))
            self.body.mount(Button("Tasks", id="tasks"))
            self.body.mount(Button("Quit", id="quit"))

        def show_queues(self) -> None:
            assert self.body
            self.body.remove_children()
            table: DataTable = DataTable()
            table.add_columns("Name", "Title", "Description")
            for q in self.manager.queue_list():
                table.add_row(q["name"], q["title"], q["description"])
            self.body.mount(table)
            # Input and button for deleting a queue
            self.body.mount(Input(placeholder="Queue name", id="del_queue_name"))
            self.body.mount(Button("Delete Queue", id="queue_delete"))
            self.body.mount(Button("Add Queue", id="queue_add"))
            self.body.mount(Button("Back", id="main"))

        def show_tasks(self) -> None:
            assert self.body
            self.body.remove_children()
            table: DataTable = DataTable()
            table.add_columns("ID", "Title", "Status")
            for t in self.manager.task_list():
                table.add_row(t["id"], t["title"], t["status"])
            self.body.mount(table)
            self.body.mount(Input(placeholder="Task ID", id="task_id"))
            self.body.mount(Button("View Comments", id="view_comments"))
            self.body.mount(Button("Delete Task", id="task_delete"))
            self.body.mount(Button("Back", id="main"))

        def show_comments(self, task_id: str) -> None:
            assert self.body
            self.body.remove_children()
            self.current_task_id = task_id
            self.body.mount(Static(f"Comments for {task_id}", classes="title"))
            comments = self.manager.task_comment_list(task_id) or []
            for c in comments:
                created = time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(c.get("created_at", 0))
                )
                self.body.mount(
                    Static(f"[{c.get('id')}] {created}: {c.get('text')}")
                )
            self.body.mount(Input(placeholder="New comment", id="new_comment"))
            self.body.mount(Button("Add Comment", id="add_comment"))
            self.body.mount(Button("Back", id="tasks"))

        def on_button_pressed(self, event: Button.Pressed) -> None:  # pragma: no cover - UI callbacks
            button_id = event.button.id
            if button_id == "quit":
                self.exit()
            elif button_id == "queues":
                self.show_queues()
            elif button_id == "tasks":
                self.show_tasks()
            elif button_id == "main":
                self.show_main()
            elif button_id == "queue_add":
                assert self.body
                self.body.remove_children()
                name_in = Input(placeholder="Queue name", id="q_name")
                title_in = Input(placeholder="Queue title", id="q_title")
                desc_in = Input(placeholder="Description", id="q_desc")
                self.body.mount(name_in)
                self.body.mount(title_in)
                self.body.mount(desc_in)
                self.body.mount(Button("Create", id="create_queue"))
                self.body.mount(Button("Back", id="queues"))
            elif button_id == "view_comments":
                task_id = self.query_one("#task_id", Input).value
                if task_id:
                    self.show_comments(task_id)
            elif button_id == "add_comment":
                assert self.current_task_id
                comment = self.query_one("#new_comment", Input).value
                if comment:
                    self.manager.task_comment_add(self.current_task_id, comment)
                self.show_comments(self.current_task_id)
            elif button_id == "queue_delete":
                name = self.query_one("#del_queue_name", Input).value
                if name:
                    self.body.remove_children()
                    self.body.mount(Static(f"Are you sure you want to delete the queue '{name}'?", classes="confirmation"))
                    self.body.mount(Button("Yes", id="confirm_delete_queue"))
                    self.body.mount(Button("No", id="queues"))
            elif button_id == "task_delete":
                task_id = self.query_one("#task_id", Input).value
                if task_id:
                    self.body.mount(Static(f"Are you sure you want to delete task '{task_id}'?", id="confirm_delete"))
                    self.body.mount(Button("Yes", id="confirm_yes"))
                    self.body.mount(Button("No", id="confirm_no"))
            elif button_id == "create_queue":
                name = self.query_one("#q_name", Input).value
                title = self.query_one("#q_title", Input).value
                desc = self.query_one("#q_desc", Input).value
                self.manager.queue_add(name, title, desc)
                self.show_queues()

    TMApp(tm).run()

