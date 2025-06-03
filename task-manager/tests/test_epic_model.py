import unittest
from task_manager.models import Epic, EpicStatus

class TestEpicModel(unittest.TestCase):
    def test_to_dict_from_dict(self):
        original = Epic(
            id="epic-1",
            title="Title",
            description="Desc",
            status=EpicStatus.OPEN,
            child_tasks=["t-1"],
            child_epics=["epic-2"],
            parent_epic=None,
            created_at=1.0,
            updated_at=2.0,
        )
        data = original.to_dict()
        self.assertEqual(data["status"], "open")
        clone = Epic.from_dict(data)
        self.assertEqual(clone, original)

if __name__ == "__main__":
    unittest.main()
