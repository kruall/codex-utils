import logging
import time
from typing import TYPE_CHECKING

from .exceptions import TaskManagerError

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
        BINDINGS = [
            ("q", "quit", "Quit"),
            ("1", "queues", "Queues"),
            ("2", "tasks", "Tasks"),
            ("escape", "main", "Back"),
        ]

        def __init__(self, manager: "TaskManager") -> None:
            super().__init__()
            self.manager = manager
            self.body: Vertical | None = None
            self.current_task_id: str | None = None

        def _parse_comment_id(self, cid_str: str) -> int | None:
            """Helper method to parse comment ID string to integer.
            
            Args:
                cid_str: The comment ID as a string
                
            Returns:
                The comment ID as an integer, or None if parsing fails
            """
            if not cid_str:
                return None
            try:
                return int(cid_str)
            except ValueError:
                return None

        def compose(self) -> ComposeResult:
            yield Header(show_clock=True)
            yield Footer()
            self.body = Vertical()
            yield self.body

        def on_mount(self) -> None:
            """Called when the app is mounted and ready."""
            self.show_main()

        def show_main(self) -> None:
            if self.body is None:
                raise RuntimeError("Body container is not initialized")
            self.body.remove_children()
            self.body.mount(Static("Task Manager", classes="title"))
            self.body.mount(Button("Queues", id="queues"))
            self.body.mount(Button("Tasks", id="tasks"))
            self.body.mount(Button("Quit", id="quit"))
            self.set_focus(self.query_one("#queues"))

        def show_error(self, message: str) -> None:
            if self.body is None:
                raise RuntimeError("Body container is not initialized")
            self.body.mount(Static(f"Error: {message}", classes="error"))

        def show_queues(self) -> None:
            if self.body is None:
                raise RuntimeError("Body container is not initialized")
            self.body.remove_children()
            table: DataTable = DataTable()
            table.add_columns("Name", "Title", "Description")
            try:
                queues = self.manager.queue_list()
            except TaskManagerError as e:
                self.show_error(str(e))
                queues = []
            for q in queues:
                table.add_row(q["name"], q["title"], q["description"])
            self.body.mount(table)
            self.set_focus(table)
            # Input and button for deleting a queue
            self.body.mount(Input(placeholder="Queue name", id="del_queue_name"))
            self.body.mount(Button("Delete Queue", id="queue_delete"))
            self.body.mount(Button("Add Queue", id="queue_add"))
            self.body.mount(Button("Back", id="main"))

        def show_tasks(self) -> None:
            if self.body is None:
                raise RuntimeError("Body container is not initialized")
            self.body.remove_children()
            table: DataTable = DataTable()
            table.add_columns("ID", "Title", "Status")
            try:
                tasks = self.manager.task_list()
            except TaskManagerError as e:
                self.show_error(str(e))
                tasks = []
            for t in tasks:
                table.add_row(t["id"], t["title"], t["status"])
            self.body.mount(table)
            self.set_focus(table)
            self.body.mount(Input(placeholder="Task ID", id="task_id"))
            self.body.mount(Button("View Comments", id="view_comments"))
            self.body.mount(Button("Delete Task", id="task_delete"))
            self.body.mount(Button("Back", id="main"))

        def show_comments(self, task_id: str) -> None:
            if self.body is None:
                raise RuntimeError("Body container is not initialized")
            self.body.remove_children()
            self.current_task_id = task_id
            self.body.mount(Static(f"Comments for {task_id}", classes="title"))
            try:
                comments = self.manager.task_comment_list(task_id) or []
            except TaskManagerError as e:
                self.show_error(str(e))
                comments = []
            for c in comments:
                created = time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(c.get("created_at", 0))
                )
                self.body.mount(
                    Static(f"[{c.get('id')}] {created}: {c.get('text')}")
                )
            self.body.mount(Input(placeholder="New comment", id="new_comment"))
            self.body.mount(Button("Add Comment", id="add_comment"))
            # Inputs for editing a comment
            self.body.mount(Input(placeholder="Comment ID", id="edit_comment_id"))
            self.body.mount(Input(placeholder="Updated text", id="edit_comment_text"))
            self.body.mount(Button("Edit Comment", id="edit_comment"))
            # Inputs for removing a comment
            self.body.mount(Input(placeholder="Comment ID", id="remove_comment_id"))
            self.body.mount(Button("Remove Comment", id="remove_comment"))
            self.body.mount(Button("Back", id="tasks"))

        def action_queues(self) -> None:
            self.show_queues()

        def action_tasks(self) -> None:
            self.show_tasks()

        def action_main(self) -> None:
            self.show_main()

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
                if self.body is None:
                    raise RuntimeError("Body container is not initialized")
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
                if self.current_task_id is None:
                    raise RuntimeError("Current task ID is not set")
                comment = self.query_one("#new_comment", Input).value
                if comment:
                    try:
                        self.manager.task_comment_add(self.current_task_id, comment)
                    except TaskManagerError as e:
                        self.show_error(str(e))
                self.show_comments(self.current_task_id)
            elif button_id == "edit_comment":
                if self.current_task_id is None:
                    raise RuntimeError("Current task ID is not set")
                cid = self.query_one("#edit_comment_id", Input).value
                text = self.query_one("#edit_comment_text", Input).value
                if cid and text:
                    cid_int = self._parse_comment_id(cid)
                    if cid_int is not None:
                        try:
                            self.manager.task_comment_edit(
                                self.current_task_id, cid_int, text
                            )
                        except TaskManagerError as e:
                            self.show_error(str(e))
                self.show_comments(self.current_task_id)
            elif button_id == "remove_comment":
                if self.current_task_id is None:
                    raise RuntimeError("Current task ID is not set")
                cid = self.query_one("#remove_comment_id", Input).value
                if cid:
                    cid_int = self._parse_comment_id(cid)
                    if cid_int is not None:
                        try:
                            self.manager.task_comment_remove(self.current_task_id, cid_int)
                        except TaskManagerError as e:
                            self.show_error(str(e))
                self.show_comments(self.current_task_id)
            elif button_id == "queue_delete":
                name = self.query_one("#del_queue_name", Input).value
                if name:
                    if self.body is None:
                        raise RuntimeError("Body container is not initialized")
                    self.body.remove_children()
                    self.body.mount(Static(f"Are you sure you want to delete the queue '{name}'?", classes="confirmation"))
                    self.body.mount(Button("Yes", id="confirm_delete_queue"))
                    self.body.mount(Button("No", id="queues"))
            elif button_id == "task_delete":
                task_id = self.query_one("#task_id", Input).value
                if task_id:
                    if self.body is None:
                        raise RuntimeError("Body container is not initialized")
                    self.body.mount(Static(f"Are you sure you want to delete task '{task_id}'?", id="confirm_delete"))
                    self.body.mount(Button("Yes", id="confirm_yes"))
                    self.body.mount(Button("No", id="confirm_no"))
            elif button_id == "create_queue":
                name = self.query_one("#q_name", Input).value
                title = self.query_one("#q_title", Input).value
                desc = self.query_one("#q_desc", Input).value
                try:
                    self.manager.queue_add(name, title, desc)
                except TaskManagerError as e:
                    self.show_error(str(e))
                self.show_queues()

    TMApp(tm).run()

