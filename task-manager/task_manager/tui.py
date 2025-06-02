import logging
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - type hints only
    from textual.app import App, ComposeResult  # type: ignore
    from textual.containers import Vertical  # type: ignore
    from textual.widgets import Header, Footer, Button, Static, Input, DataTable  # type: ignore
    from textual.screen import Screen  # type: ignore
from .core import TaskManager
from .exceptions import TaskManagerError

try:
    from textual.app import App, ComposeResult  # type: ignore
    from textual.containers import Vertical  # type: ignore
    from textual.widgets import Header, Footer, Button, Static, Input, DataTable  # type: ignore
    from textual.screen import Screen  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    logging.getLogger(__name__).error(
        "Textual is required for the UI. Install with 'pip install textual'"
    )
    def launch_tui(tm: "TaskManager") -> None:
        return
else:

    def _parse_comment_id(cid_str: str) -> int | None:
        """Parse a comment ID string to int."""
        if not cid_str:
            return None
        try:
            return int(cid_str)
        except ValueError:
            return None

    class BaseScreen(Screen):
        def __init__(self, manager: "TaskManager") -> None:
            super().__init__()
            self.manager = manager

        def compose(self) -> ComposeResult:
            yield Header()
            with Vertical(id="main"):
                self.body = Vertical(id="body")
                yield self.body
            yield Footer()

        def on_button_pressed(self, event: Button.Pressed) -> None:  # pragma: no cover - UI callbacks
            bid = event.button.id
            if bid == "back":
                self.app.pop_screen()
            elif bid == "quit":
                self.app.exit()

        def show_error(self, message: str) -> None:
            # Simple error display - could be enhanced with a modal
            if hasattr(self, 'body') and self.body:
                self.body.mount(Static(f"Error: {message}", classes="error"))

        def _handle_manager_operation(self, operation_func, *args, **kwargs):
            """Helper method to handle manager operations with consistent error handling."""
            try:
                return operation_func(*args, **kwargs)
            except (TaskManagerError, ValueError) as e:
                self.show_error(str(e))
                return None

    class MainScreen(BaseScreen):
        def on_mount(self) -> None:
            assert self.body is not None
            self.body.mount(Static("Task Manager", classes="title"))
            self.body.mount(Button("Queues", id="queues"))
            self.body.mount(Button("Tasks", id="tasks"))
            self.body.mount(Button("Quit", id="quit"))
            self.set_focus(self.query_one("#queues"))

        def on_button_pressed(self, event: Button.Pressed) -> None:  # pragma: no cover - UI callbacks
            bid = event.button.id
            if bid == "queues":
                self.app.push_screen(QueuesScreen(self.manager))
            elif bid == "tasks":
                self.app.push_screen(TasksScreen(self.manager))
            elif bid == "quit":
                self.app.exit()

    class QueuesScreen(BaseScreen):
        def on_mount(self) -> None:
            self.refresh_screen()

        def refresh_screen(self) -> None:
            assert self.body is not None
            self.body.remove_children()
            table: DataTable = DataTable()
            table.add_columns("Name", "Title", "Description")
            for q in self.manager.queue_list():
                table.add_row(q["name"], q["title"], q["description"])
            self.body.mount(table)
            self.set_focus(table)
            self.body.mount(Input(placeholder="Queue name", id="del_queue_name"))
            self.body.mount(Button("Delete Queue", id="queue_delete"))
            self.body.mount(Button("Add Queue", id="queue_add"))
            self.body.mount(Button("Back", id="back"))

        def on_button_pressed(self, event: Button.Pressed) -> None:  # pragma: no cover - UI callbacks
            super().on_button_pressed(event)  # Handle common actions
            bid = event.button.id
            if bid == "back":
                self.app.pop_screen()
            elif bid == "queue_add":
                assert self.body is not None
                self.body.remove_children()
                self.body.mount(Input(placeholder="Queue name", id="q_name"))
                self.body.mount(Input(placeholder="Queue title", id="q_title"))
                self.body.mount(Input(placeholder="Description", id="q_desc"))
                self.body.mount(Button("Create", id="create_queue"))
                self.body.mount(Button("Back", id="cancel"))
            elif bid == "create_queue":
                name = self.query_one("#q_name", Input).value
                title = self.query_one("#q_title", Input).value
                desc = self.query_one("#q_desc", Input).value
                self._handle_manager_operation(self.manager.queue_add, name, title, desc)
                self.refresh_screen()
            elif bid == "cancel":
                self.refresh_screen()
            elif bid == "queue_delete":
                name = self.query_one("#del_queue_name", Input).value
                if name:
                    assert self.body is not None
                    self.body.remove_children()
                    self.body.mount(
                        Static(
                            f"Are you sure you want to delete the queue '{name}'?",
                            classes="confirmation",
                        )
                    )
                    self.body.mount(Button("Yes", id="confirm_delete"))
                    self.body.mount(Button("No", id="cancel"))
                    self._delete_target = name
            elif bid == "confirm_delete":
                delete_name: str | None = getattr(self, "_delete_target", None)
                if delete_name:
                    self._handle_manager_operation(self.manager.queue_delete, delete_name)
                self.refresh_screen()

    class TasksScreen(BaseScreen):
        def on_mount(self) -> None:
            self.refresh_screen()

        def refresh_screen(self) -> None:
            assert self.body is not None
            self.body.remove_children()
            table: DataTable = DataTable()
            table.add_columns("ID", "Title", "Status")
            for t in self.manager.task_list():
                table.add_row(t["id"], t["title"], t["status"])
            self.body.mount(table)
            self.set_focus(table)
            self.body.mount(Input(placeholder="Task ID", id="task_id"))
            self.body.mount(Button("View Comments", id="view_comments"))
            self.body.mount(Button("Delete Task", id="task_delete"))
            self.body.mount(Button("Back", id="back"))

        def on_button_pressed(self, event: Button.Pressed) -> None:  # pragma: no cover - UI callbacks
            super().on_button_pressed(event)  # Handle common actions
            bid = event.button.id
            if bid == "back":
                self.app.pop_screen()
            elif bid == "view_comments":
                task_id = self.query_one("#task_id", Input).value
                if task_id:
                    # Validate task exists before navigating
                    if self._handle_manager_operation(self.manager.task_show, task_id) is not None:
                        self.app.push_screen(CommentsScreen(self.manager, task_id))
            elif bid == "task_delete":
                task_id = self.query_one("#task_id", Input).value
                if task_id:
                    assert self.body is not None
                    self.body.remove_children()
                    self.body.mount(
                        Static(
                            f"Are you sure you want to delete task '{task_id}'?",
                            id="confirm_delete",
                        )
                    )
                    self.body.mount(Button("Yes", id="confirm_task_delete"))
                    self.body.mount(Button("No", id="cancel"))
                    self._delete_target = task_id
            elif bid == "confirm_task_delete":
                tid: str | None = getattr(self, "_delete_target", None)
                if tid:
                    self._handle_manager_operation(self.manager.task_delete, tid)
                self.refresh_screen()
            elif bid == "cancel":
                self.refresh_screen()

    class CommentsScreen(BaseScreen):
        def __init__(self, manager: "TaskManager", task_id: str) -> None:
            super().__init__(manager)
            self.task_id = task_id

        def on_mount(self) -> None:
            self.refresh_screen()

        def refresh_screen(self) -> None:
            assert self.body is not None
            self.body.remove_children()
            self.body.mount(Static(f"Comments for {self.task_id}", classes="title"))
            comments = self._handle_manager_operation(self.manager.task_comment_list, self.task_id) or []
            for c in comments:
                created = time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(c.get("created_at", 0))
                )
                self.body.mount(
                    Static(f"[{c.get('id')}] {created}: {c.get('text')}")
                )
            self.body.mount(Input(placeholder="New comment", id="new_comment"))
            self.body.mount(Button("Add Comment", id="add_comment"))
            self.body.mount(Input(placeholder="Comment ID", id="edit_comment_id"))
            self.body.mount(Input(placeholder="Updated text", id="edit_comment_text"))
            self.body.mount(Button("Edit Comment", id="edit_comment"))
            self.body.mount(Input(placeholder="Comment ID", id="remove_comment_id"))
            self.body.mount(Button("Remove Comment", id="remove_comment"))
            self.body.mount(Button("Back", id="back"))

        def on_button_pressed(self, event: Button.Pressed) -> None:  # pragma: no cover - UI callbacks
            bid = event.button.id
            if bid == "back":
                self.app.pop_screen()
            elif bid == "add_comment":
                comment = self.query_one("#new_comment", Input).value
                if comment:
                    self._handle_manager_operation(self.manager.task_comment_add, self.task_id, comment)
                self.refresh_screen()
            elif bid == "edit_comment":
                cid = self.query_one("#edit_comment_id", Input).value
                text = self.query_one("#edit_comment_text", Input).value
                if cid and text:
                    cid_int = _parse_comment_id(cid)
                    if cid_int is not None:
                        self._handle_manager_operation(self.manager.task_comment_edit, self.task_id, cid_int, text)
                self.refresh_screen()
            elif bid == "remove_comment":
                cid = self.query_one("#remove_comment_id", Input).value
                if cid:
                    cid_int = _parse_comment_id(cid)
                    if cid_int is not None:
                        self._handle_manager_operation(self.manager.task_comment_remove, self.task_id, cid_int)
                self.refresh_screen()

    class TMApp(App):
        TITLE = "Task Manager"
        BINDINGS = [
            ("q", "quit", "Quit"),
            ("1", "queues", "Queues"),
            ("2", "tasks", "Tasks"),
            ("escape", "main", "Back"),
        ]

        def __init__(self, manager: "TaskManager") -> None:
            super().__init__()
            self.manager = manager

        def action_main(self) -> None:
            self.push_screen(MainScreen(self.manager))

        def action_queues(self) -> None:
            self.push_screen(QueuesScreen(self.manager))

        def action_tasks(self) -> None:
            self.push_screen(TasksScreen(self.manager))

        def on_mount(self) -> None:
            self.action_main()

    def launch_tui(tm: "TaskManager") -> None:
        TMApp(tm).run()
