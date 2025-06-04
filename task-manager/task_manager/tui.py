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
    def _launch_tui_noop(tm: "TaskManager") -> None:
        return

    launch_tui = _launch_tui_noop
else:
    from textual.message import Message

    def _parse_comment_id(cid_str: str) -> int | None:
        """Parse a comment ID string to int."""
        if not cid_str:
            return None
        try:
            return int(cid_str)
        except ValueError:
            return None

    class Back(Message):
        """Signal that the user requested to go back."""

    class Quit(Message):
        """Signal that the application should exit."""

    class Queues(Message):
        """Navigate to the queues screen."""

    class Epics(Message):
        """Navigate to the epics screen."""

    class Tasks(Message):
        """Navigate to the tasks screen."""

    class QueueAdd(Message):
        """Show the add queue form."""

    class CreateQueue(Message):
        def __init__(self, name: str, title: str, desc: str) -> None:
            super().__init__()
            self.name = name
            self.title = title
            self.desc = desc

    class Cancel(Message):
        """Cancel the current action."""

    class QueueDelete(Message):
        def __init__(self, name: str) -> None:
            super().__init__()
            self.name = name

    class ConfirmDelete(Message):
        """Confirm queue deletion."""

    class ViewComments(Message):
        def __init__(self, task_id: str) -> None:
            super().__init__()
            self.task_id = task_id

    class TaskDelete(Message):
        def __init__(self, task_id: str) -> None:
            super().__init__()
            self.task_id = task_id

    class ViewTask(Message):
        def __init__(self, task_id: str) -> None:
            super().__init__()
            self.task_id = task_id

    class ViewEpic(Message):
        def __init__(self, epic_id: str) -> None:
            super().__init__()
            self.epic_id = epic_id

    class ConfirmTaskDelete(Message):
        """Confirm task deletion."""

    class AddComment(Message):
        def __init__(self, text: str) -> None:
            super().__init__()
            self.text = text

    class EditComment(Message):
        def __init__(self, cid: int, text: str) -> None:
            super().__init__()
            self.cid = cid
            self.text = text

    class RemoveComment(Message):
        def __init__(self, cid: int) -> None:
            super().__init__()
            self.cid = cid

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
                self.post_message(Back())
            elif bid == "quit":
                self.post_message(Quit())

        def on_back(self, message: Back) -> None:  # pragma: no cover - UI callbacks
            self.app.pop_screen()

        def on_quit(self, message: Quit) -> None:  # pragma: no cover - UI callbacks
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
            self.body.mount(Button("Epics", id="epics"))
            self.body.mount(Button("Quit", id="quit"))
            self.set_focus(self.query_one("#queues"))

        def on_button_pressed(self, event: Button.Pressed) -> None:  # pragma: no cover - UI callbacks
            super().on_button_pressed(event)
            bid = event.button.id
            if bid == "queues":
                self.post_message(Queues())
            elif bid == "tasks":
                self.post_message(Tasks())
            elif bid == "epics":
                self.post_message(Epics())

        def on_queues(self, message: Queues) -> None:  # pragma: no cover - UI callbacks
            self.app.push_screen(QueuesScreen(self.manager))

        def on_tasks(self, message: Tasks) -> None:  # pragma: no cover - UI callbacks
            self.app.push_screen(TasksScreen(self.manager))

        def on_epics(self, message: Epics) -> None:  # pragma: no cover - UI callbacks
            self.app.push_screen(EpicsScreen(self.manager))

    class QueuesScreen(BaseScreen):
        def __init__(self, manager: "TaskManager") -> None:
            super().__init__(manager)
            self._delete_target: str | None = None

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
            if bid == "queue_add":
                self.post_message(QueueAdd())
            elif bid == "create_queue":
                name = self.query_one("#q_name", Input).value
                title = self.query_one("#q_title", Input).value
                desc = self.query_one("#q_desc", Input).value
                if name and title:
                    self.post_message(CreateQueue(name, title, desc))
            elif bid == "queue_delete":
                queue_name = self.query_one("#del_queue_name", Input).value
                if queue_name:
                    self.post_message(QueueDelete(queue_name))
            elif bid == "confirm_delete":
                self.post_message(ConfirmDelete())
            elif bid == "cancel":
                self.post_message(Cancel())

        def on_queue_add(self, message: QueueAdd) -> None:  # pragma: no cover - UI callbacks
            assert self.body is not None
            self.body.remove_children()
            self.body.mount(Static("Add New Queue", classes="title"))
            self.body.mount(Input(placeholder="Queue name", id="q_name"))
            self.body.mount(Input(placeholder="Queue title", id="q_title"))
            self.body.mount(Input(placeholder="Queue description", id="q_desc"))
            self.body.mount(Button("Create", id="create_queue"))
            self.body.mount(Button("Cancel", id="cancel"))

        def on_create_queue(self, message: CreateQueue) -> None:  # pragma: no cover - UI callbacks
            self._handle_manager_operation(
                self.manager.queue_add, message.name, message.title, message.desc
            )
            self.refresh_screen()

        def on_cancel(self, message: Cancel) -> None:  # pragma: no cover - UI callbacks
            self.refresh_screen()

        def on_queue_delete(self, message: QueueDelete) -> None:  # pragma: no cover - UI callbacks
            assert self.body is not None
            self.body.remove_children()
            self.body.mount(
                Static(
                    f"Are you sure you want to delete queue '{message.name}'?",
                    id="confirm_delete",
                )
            )
            self.body.mount(Button("Yes", id="confirm_delete"))
            self.body.mount(Button("No", id="cancel"))
            self._delete_target = message.name

        def on_confirm_delete(self, message: ConfirmDelete) -> None:  # pragma: no cover - UI callbacks
            delete_name: str | None = getattr(self, "_delete_target", None)
            if delete_name:
                self._handle_manager_operation(self.manager.queue_delete, delete_name)
            self._delete_target = None
            self.refresh_screen()

    class TasksScreen(BaseScreen):
        def __init__(self, manager: "TaskManager") -> None:
            super().__init__(manager)
            self._delete_target: str | None = None

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
            self.body.mount(Button("View Task", id="view_task"))
            self.body.mount(Button("View Comments", id="view_comments"))
            self.body.mount(Button("Delete Task", id="task_delete"))
            self.body.mount(Button("Back", id="back"))

        def on_button_pressed(self, event: Button.Pressed) -> None:  # pragma: no cover - UI callbacks
            super().on_button_pressed(event)  # Handle common actions
            bid = event.button.id
            if bid == "view_comments":
                task_id = self.query_one("#task_id", Input).value
                if task_id:
                    self.post_message(ViewComments(task_id))
            elif bid == "view_task":
                task_id = self.query_one("#task_id", Input).value
                if task_id:
                    self.post_message(ViewTask(task_id))
            elif bid == "task_delete":
                task_id = self.query_one("#task_id", Input).value
                if task_id:
                    self.post_message(TaskDelete(task_id))
            elif bid == "confirm_task_delete":
                self.post_message(ConfirmTaskDelete())
            elif bid == "cancel":
                self.post_message(Cancel())

        def on_view_comments(self, message: ViewComments) -> None:  # pragma: no cover - UI callbacks
            if self._handle_manager_operation(self.manager.task_show, message.task_id) is not None:
                self.app.push_screen(CommentsScreen(self.manager, message.task_id))

        def on_view_task(self, message: ViewTask) -> None:  # pragma: no cover - UI callbacks
            if self._handle_manager_operation(self.manager.task_show, message.task_id) is not None:
                self.app.push_screen(TaskDetailScreen(self.manager, message.task_id))

        def on_task_delete(self, message: TaskDelete) -> None:  # pragma: no cover - UI callbacks
            assert self.body is not None
            self.body.remove_children()
            self.body.mount(
                Static(
                    f"Are you sure you want to delete task '{message.task_id}'?",
                    id="confirm_delete",
                )
            )
            self.body.mount(Button("Yes", id="confirm_task_delete"))
            self.body.mount(Button("No", id="cancel"))
            self._delete_target = message.task_id

        def on_confirm_task_delete(self, message: ConfirmTaskDelete) -> None:  # pragma: no cover - UI callbacks
            tid: str | None = getattr(self, "_delete_target", None)
            if tid:
                self._handle_manager_operation(self.manager.task_delete, tid)
            self._delete_target = None
            self.refresh_screen()

    class EpicsScreen(BaseScreen):
        def __init__(self, manager: "TaskManager") -> None:
            super().__init__(manager)

        def on_mount(self) -> None:
            self.refresh_screen()

        def _progress(self, epic: dict) -> str:
            done = 0
            total = len(epic.get("child_tasks", [])) + len(epic.get("child_epics", []))
            for tid in epic.get("child_tasks", []):
                data = self._handle_manager_operation(self.manager.task_show, tid)
                if data and data.get("status") == "done":
                    done += 1
            for eid in epic.get("child_epics", []):
                data = self._handle_manager_operation(self.manager.epic_show, eid)
                if data and data.get("status") == "closed":
                    done += 1
            if total == 0:
                return "0/0"
            return f"{done}/{total}"

        def refresh_screen(self) -> None:
            assert self.body is not None
            self.body.remove_children()
            table: DataTable = DataTable()
            table.add_columns("ID", "Title", "Status", "Progress")
            for e in self.manager.epic_list():
                table.add_row(e["id"], e["title"], e["status"], self._progress(e))
            self.body.mount(table)
            self.set_focus(table)
            self.body.mount(Input(placeholder="Epic ID", id="epic_id"))
            self.body.mount(Button("View Epic", id="view_epic"))
            self.body.mount(Button("Back", id="back"))

        def on_button_pressed(self, event: Button.Pressed) -> None:  # pragma: no cover - UI callbacks
            super().on_button_pressed(event)
            bid = event.button.id
            if bid == "view_epic":
                epic_id = self.query_one("#epic_id", Input).value
                if epic_id:
                    self.post_message(ViewEpic(epic_id))

        def on_view_epic(self, message: ViewEpic) -> None:  # pragma: no cover - UI callbacks
            if self._handle_manager_operation(self.manager.epic_show, message.epic_id) is not None:
                self.app.push_screen(EpicDetailScreen(self.manager, message.epic_id))

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
            super().on_button_pressed(event)
            bid = event.button.id
            if bid == "add_comment":
                comment = self.query_one("#new_comment", Input).value
                if comment:
                    self.post_message(AddComment(comment))
            elif bid == "edit_comment":
                cid = self.query_one("#edit_comment_id", Input).value
                text = self.query_one("#edit_comment_text", Input).value
                if cid and text:
                    cid_int = _parse_comment_id(cid)
                    if cid_int is not None:
                        self.post_message(EditComment(cid_int, text))
            elif bid == "remove_comment":
                cid = self.query_one("#remove_comment_id", Input).value
                if cid:
                    cid_int = _parse_comment_id(cid)
                    if cid_int is not None:
                        self.post_message(RemoveComment(cid_int))

        def on_add_comment(self, message: AddComment) -> None:  # pragma: no cover - UI callbacks
            self._handle_manager_operation(
                self.manager.task_comment_add, self.task_id, message.text
            )
            self.refresh_screen()

        def on_edit_comment(self, message: EditComment) -> None:  # pragma: no cover - UI callbacks
            self._handle_manager_operation(
                self.manager.task_comment_edit, self.task_id, message.cid, message.text
            )
            self.refresh_screen()

        def on_remove_comment(self, message: RemoveComment) -> None:  # pragma: no cover - UI callbacks
            self._handle_manager_operation(
                self.manager.task_comment_remove, self.task_id, message.cid
            )
            self.refresh_screen()

    class TaskDetailScreen(BaseScreen):
        def __init__(self, manager: "TaskManager", task_id: str) -> None:
            super().__init__(manager)
            self.task_id = task_id

        def _build_epic_chain(self, epic_id: str) -> str:
            """Return full hierarchy string for ``epic_id`` with cycle detection."""
            chain: list[str] = []
            current_id = epic_id
            visited: set[str] = set()
            while current_id and current_id not in visited:
                visited.add(current_id)
                data = self._handle_manager_operation(self.manager.epic_show, current_id)
                if not data:
                    break
                chain.append(f"{data['title']}({current_id})")
                current_id = data.get("parent_epic")
            if current_id and current_id in visited:
                chain.append("...")
            return " > ".join(reversed(chain))

        def on_mount(self) -> None:
            self.refresh_screen()

        def refresh_screen(self) -> None:
            assert self.body is not None
            self.body.remove_children()
            data = self._handle_manager_operation(self.manager.task_show, self.task_id)
            if not data:
                return
            self.body.mount(Static(f"Task {data['id']}", classes="title"))
            self.body.mount(Static(f"Title: {data['title']}"))
            self.body.mount(Static(f"Status: {data['status']}"))
            epics = self._handle_manager_operation(
                self.manager.task_parent_epics, self.task_id
            ) or []
            if epics:
                self.body.mount(Static("Epics:", classes="title"))
                for e in epics:
                    eid = e["id"]
                    edata = self._handle_manager_operation(self.manager.epic_show, eid)
                    if not edata:
                        continue
                    hierarchy = self._build_epic_chain(eid)
                    label = f"{eid}: {edata['title']} ({edata['status']})"
                    self.body.mount(Button(label, id=f"open_epic_{eid}"))
                    self.body.mount(Static(hierarchy))
                    self.body.mount(Static(edata.get("description", "")))
                    if edata.get("child_tasks"):
                        self.body.mount(Static("Tasks:", classes="title"))
                        for tid in edata["child_tasks"]:
                            tdata = self._handle_manager_operation(self.manager.task_show, tid)
                            if not tdata:
                                continue
                            tlabel = f"{tid}: {tdata['title']} ({tdata['status']})"
                            self.body.mount(Button(tlabel, id=f"open_task_{tid}"))
                    if edata.get("child_epics"):
                        self.body.mount(Static("Child Epics:", classes="title"))
                        for ceid in edata["child_epics"]:
                            cdata = self._handle_manager_operation(self.manager.epic_show, ceid)
                            if not cdata:
                                continue
                            clabel = f"{ceid}: {cdata['title']} ({cdata['status']})"
                            self.body.mount(Button(clabel, id=f"open_epic_{ceid}"))
            self.body.mount(Button("View Comments", id="view_comments"))
            self.body.mount(Button("Back", id="back"))

        def on_button_pressed(self, event: Button.Pressed) -> None:  # pragma: no cover - UI callbacks
            super().on_button_pressed(event)
            bid = event.button.id or ""
            if bid == "view_comments":
                self.post_message(ViewComments(self.task_id))
            elif bid.startswith("open_task_"):
                self.post_message(ViewTask(bid.split("_", 2)[2]))
            elif bid.startswith("open_epic_"):
                self.post_message(ViewEpic(bid.split("_", 2)[2]))

        def on_view_comments(self, message: ViewComments) -> None:  # pragma: no cover - UI callbacks
            self.app.push_screen(CommentsScreen(self.manager, self.task_id))

        def on_view_epic(self, message: ViewEpic) -> None:  # pragma: no cover - UI callbacks
            self.app.push_screen(EpicDetailScreen(self.manager, message.epic_id))

        def on_view_task(self, message: ViewTask) -> None:  # pragma: no cover - UI callbacks
            if (
                self._handle_manager_operation(
                    self.manager.task_show, message.task_id
                )
                is not None
            ):
                self.app.push_screen(TaskDetailScreen(self.manager, message.task_id))

    class EpicDetailScreen(BaseScreen):
        def __init__(self, manager: "TaskManager", epic_id: str) -> None:
            super().__init__(manager)
            self.epic_id = epic_id

        def on_mount(self) -> None:
            self.refresh_screen()

        def refresh_screen(self) -> None:
            assert self.body is not None
            self.body.remove_children()
            data = self._handle_manager_operation(self.manager.epic_show, self.epic_id)
            if not data:
                return
            self.body.mount(Static(f"Epic {data['id']}", classes="title"))
            self.body.mount(Static(f"Title: {data['title']}"))
            self.body.mount(Static(f"Status: {data['status']}"))
            if data.get("parent_epic"):
                self.body.mount(Button(f"Parent: {data['parent_epic']}", id=f"open_epic_{data['parent_epic']}"))
            if data.get("child_tasks"):
                self.body.mount(Static("Tasks:", classes="title"))
                for tid in data["child_tasks"]:
                    self.body.mount(Button(tid, id=f"open_task_{tid}"))
            if data.get("child_epics"):
                self.body.mount(Static("Child Epics:", classes="title"))
                for eid in data["child_epics"]:
                    self.body.mount(Button(eid, id=f"open_epic_{eid}"))
            self.body.mount(Button("Back", id="back"))

        def on_button_pressed(self, event: Button.Pressed) -> None:  # pragma: no cover - UI callbacks
            super().on_button_pressed(event)
            bid = event.button.id or ""
            if bid.startswith("open_task_"):
                self.post_message(ViewTask(bid.split("_", 2)[2]))
            elif bid.startswith("open_epic_"):
                self.post_message(ViewEpic(bid.split("_", 2)[2]))

        def on_view_task(self, message: ViewTask) -> None:  # pragma: no cover - UI callbacks
            self.app.push_screen(TaskDetailScreen(self.manager, message.task_id))

        def on_view_epic(self, message: ViewEpic) -> None:  # pragma: no cover - UI callbacks
            self.app.push_screen(EpicDetailScreen(self.manager, message.epic_id))

    class TMApp(App):
        TITLE = "Task Manager"
        BINDINGS = [
            ("q", "quit", "Quit"),
            ("1", "queues", "Queues"),
            ("2", "tasks", "Tasks"),
            ("3", "epics", "Epics"),
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

        def action_epics(self) -> None:
            self.push_screen(EpicsScreen(self.manager))

        def on_mount(self) -> None:
            self.action_main()

    def launch_tui(tm: "TaskManager") -> None:
        TMApp(tm).run()
