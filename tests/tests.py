import unittest
import os
from KvickStore import KvickStore


class TestKvickStore(unittest.TestCase):
    def setUp(self):
        # Setup a test database file
        self.test_db_file = "test_kvickstore.db"
        self.store = KvickStore(self.test_db_file, auto_save=True)

    def tearDown(self):
        # Clean up the test database file
        try:
            os.remove(self.test_db_file)
        except FileNotFoundError:
            pass

    def test_set_and_get(self):
        # Test setting and getting values
        self.store.set("test_key", "test_value")
        self.assertEqual(self.store.get("test_key"), "test_value")

    def test_delitem(self):
        # Test deleting an item
        self.store.set("delete_me", "to be deleted")
        self.store.__delitem__("delete_me")
        self.assertFalse(self.store.exists("delete_me"))

    def test_len(self):
        # Test the length functionality
        self.store.set("len_test1", "value1")
        self.store.set("len_test2", "value2")
        self.assertEqual(len(self.store), 2)

    def test_in_operator(self):
        # Test the in operator
        self.store.set("in_test", "value")
        self.assertTrue("in_test" in self.store)

    def test_auto_save(self):
        # Test auto-save functionality by creating a new instance and checking if data persists
        self.store.set("auto_save_test", "value")
        del self.store  # Attempt to trigger auto-save on deletion

        # Create a new instance to check for persisted data
        new_store = KvickStore(self.test_db_file)
        self.assertTrue(new_store.get("auto_save_test"), "value")

    def test_list_operations(self):
        # Test list related operations
        self.store.list_create("my_list")
        self.store.list_add("my_list", "item1")
        self.store.list_add("my_list", "item2")
        retrieved_list = self.store.list_getall("my_list")
        self.assertListEqual(retrieved_list, ["item1", "item2"])

    def test_add_to_str_or_num(self):
        # Test adding to a string or number
        self.store.set("my_num", 10)
        self.store.add_to_str_or_num("my_num", 5)
        self.assertEqual(self.store.get("my_num"), 15)

        self.store.set("my_str", "Hello")
        self.store.add_to_str_or_num("my_str", " World")
        self.assertEqual(self.store.get("my_str"), "Hello World")

    def test_nonexistent_key(self):
        # Test handling of nonexistent keys
        self.assertFalse(self.store.get("nonexistent"))
        self.assertFalse(self.store.rm("nonexistent"))

    def test_invalid_key(self):
        # Test handling of invalid keys
        with self.assertRaises(TypeError):
            self.store.set(None, "value")

        with self.assertRaises(ValueError):
            self.store.set("~num~invalid", "value")


if __name__ == "__main__":
    unittest.main()
