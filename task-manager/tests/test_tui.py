import tempfile
import unittest
from task_manager.core import TaskManager
from task_manager.tui import (
    TMApp,
    MainScreen,
    QueuesScreen,
    TasksScreen,
    EpicsScreen,
    TaskDetailScreen,
    EpicDetailScreen,
)


class TestTuiNavigation(unittest.IsolatedAsyncioTestCase):
    async def test_basic_navigation(self) -> None:
        tasks_dir = tempfile.mkdtemp()
        epics_dir = tempfile.mkdtemp()
        manager = TaskManager(tasks_dir, epics_root=epics_dir)
        async with TMApp(manager).run_test() as pilot:
            # Should start on main screen
            self.assertIsInstance(pilot.app.screen, MainScreen)

            # Open queues screen and return
            await pilot.press("1")
            await pilot.pause()
            self.assertIsInstance(pilot.app.screen, QueuesScreen)

            await pilot.press("escape")
            await pilot.pause()
            self.assertIsInstance(pilot.app.screen, MainScreen)

            # Open tasks screen
            await pilot.press("2")
            await pilot.pause()
            self.assertIsInstance(pilot.app.screen, TasksScreen)

            # Open epics screen
            await pilot.press("3")
            await pilot.pause()
            self.assertIsInstance(pilot.app.screen, EpicsScreen)

            # Quit the application
            await pilot.press("q")


class TestTaskEpicNavigation(unittest.IsolatedAsyncioTestCase):
    async def test_task_epic_navigation(self) -> None:
        tasks_dir = tempfile.mkdtemp()
        epics_dir = tempfile.mkdtemp()
        manager = TaskManager(tasks_dir, epics_root=epics_dir)
        manager.queue_add("q", "Q", "d")
        tid = manager.task_add("T", "d", "q")
        eid = manager.epic_add("E", "d")
        manager.epic_add_task(eid, tid)
        async with TMApp(manager).run_test() as pilot:
            await pilot.press("2")
            await pilot.pause()
            self.assertIsInstance(pilot.app.screen, TasksScreen)
            from textual.widgets import Input
            input_widget = pilot.app.screen.query_one("#task_id", Input)
            input_widget.value = tid
            await pilot.click("#view_task")
            await pilot.pause()
            self.assertIsInstance(pilot.app.screen, TaskDetailScreen)
            await pilot.click(f"#open_epic_{eid}")
            await pilot.pause()
            self.assertIsInstance(pilot.app.screen, EpicDetailScreen)
            await pilot.press("q")

