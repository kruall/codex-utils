import tempfile
import unittest
from task_manager.core import TaskManager
from task_manager.tui import TMApp, MainScreen, QueuesScreen, TasksScreen


class TestTuiNavigation(unittest.IsolatedAsyncioTestCase):
    async def test_basic_navigation(self) -> None:
        tasks_dir = tempfile.mkdtemp()
        manager = TaskManager(tasks_dir)
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

            # Quit the application
            await pilot.press("q")

