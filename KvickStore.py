from typing import Union, Any, Iterable
import ast
import os
import json
from threading import Thread
from tempfile import NamedTemporaryFile
import signal
import sys


class KvickStore:
    def __init__(self, location: str, auto_save: bool = False):
        self.load(location, auto_save)
        self.save_thread = None
        self.set_sigterm_handler()

    def __setitem__(self, key: Union[int, float, str, list, tuple], val: Any) -> Any:
        """
        Allows the use of the [] operator to set a value
        """
        self.set(key, val)

    def __getitem__(self, key: Union[int, float, str, list, tuple]) -> Any:
        """
        Allows the use of the [] operator to get a value
        """
        return self.get(key)

    def __delitem__(self, key: Union[int, float, str, list, tuple]) -> Any:
        """
        Allows the use of the del operator to remove a key-value pair
        """
        return self.rm(key)

    def __len__(self) -> int:
        """
        Allows the use of the len() function to get the number of keys
        """
        return self.totalkeys()

    def __contains__(self, key: Union[int, float, str, list, tuple]) -> bool:
        """
        Allows the use of the in operator to check if a key exists
        """
        return self.exists(key)

    def set_sigterm_handler(self) -> None:
        """
        Assigns a handler to the SIGTERM signal to save the data store (during self.save) before the program exits
        """

        def sigterm_handler(*args, **kwargs):
            if self.save_thread is not None:
                self.save_thread.join()
            sys.exit(0)

        signal.signal(signal.SIGTERM, sigterm_handler)

    def load(self, location: str, auto_save: bool = False) -> None:
        """
        Loads a data store from a file. If the file does not exist, a new data store is created.
        """
        self.location = os.path.expanduser(location)
        self.auto_save = auto_save

        if os.path.exists(self.location):
            self._load()
        else:
            self.db = {}

    def _load(self) -> None:
        """
        Load data store from a file.
        If the file is empty, a new data store is created.
        """
        try:
            with open(self.location, "r") as f:
                self.db = json.load(f)

        except ValueError:
            if os.stat(self.location).st_size == 0:
                self.db = {}
            else:
                raise ValueError("Invalid JSON format")

    def _save(self) -> None:
        """
        Save to a temp file then move to the real file.
        """
        with NamedTemporaryFile(mode="w", delete=False) as f:
            json.dump(self.db, f)
        if os.stat(f.name).st_size != 0:
            os.replace(f.name, self.location)

    def save(self) -> None:
        """
        Saves the data store to a file.
        """
        self.save_thread = Thread(target=self._save)
        self.save_thread.start()
        self.save_thread.join()

    def _auto_save(self) -> None:
        """
        Save to file if auto_save is on
        """
        if self.auto_save:
            self.save()

    def _check_key_format_error(self, key: Union[int, float, str, list, tuple]) -> None:
        """
        Internal function to raise a TypeError or ValueError if the key is of an invalid type or format
        """
        if not isinstance(key, (int, float, str, list, tuple)):
            raise TypeError("Key must be of type int, str or tuple")

        if isinstance(key, str) and key.startswith("~num~"):
            raise ValueError("Key cannot start with ~num~ (reserved for internal use)")

    def _transform_key_forward(self, key: Union[int, float, str, list, tuple]) -> str:
        """
        Internal function to transform the key to a string for JSON serialization
        """
        if isinstance(key, (list, tuple)):
            return str(key)
        if isinstance(key, (float, int)):
            return "~num~" + str(key)
        return key

    def _transform_key_backward(self, key: str) -> Union[int, float, str, list, tuple]:
        """
        Internal function to transform the key back to its original type
        """
        if key.startswith("~num~"):
            return ast.literal_eval(key[5:])
        if key.startswith("("):
            return tuple(key[1:-1].split(", "))
        if key.startswith("["):
            return list(key[1:-1].split(", "))
        return key

    def set(self, key: Union[int, float, str, list, tuple], val: Any) -> None:
        """
        Sets a value in the data store.

        This method assigns a given value to a specified key within the data store.
        If the key already exists, the existing value will be overwritten with the new value.

        Parameters:
        - key (Union[int, float, str, list, tuple]): The key under which the value is stored. The key must be of type int, str, or tuple. If a key of a different type is provided, a TypeError will be raised.
        - val (Any): The value to be stored in the data store.

        Returns:
        - None: The method does not return any value.

        Raises:
        - TypeError: If the provided key is not of type int, str, or tuple.
        - ValueError: If the provided key is a string and starts with "~num~".

        Note:
        Cannot have a string key that starts with "~num~" as it is reserved for internal use.
        Tuples when stored as values will be converted to lists. When retrieved, the value will be a list. This is due to the fact that JSON does not support the storage of tuples.
        Due to JSON limitations, if a dictionary is stored as a value, trying to have non-string keys will raise a TypeError.
        The method internally transforms the key using a private method `_transform_key_forward` before storing the value in the database. This transformation is applied to ensure the key conforms to the storage requirements of the data store.
        """

        self._check_key_format_error(key)

        self.db[self._transform_key_forward(key)] = val
        self._auto_save()

    def get(self, key: Union[int, float, str, list, tuple]) -> Any:
        """
        Retrieves a value from the data store based on the given key.

        This method looks up a value in the data store using the specified key.
        If the key exists, the corresponding value is returned.
        If the key does not exist, the method returns False, indicating the absence of a value for the given key.

        Parameters:
        - key (Union[int, float, str, list, tuple]): The key for which the value is to be retrieved. The key must be of type int, str, or tuple. If a key of a different type is provided, a TypeError will be raised.

        Returns:
        - Any: The value associated with the given key in the data store. If the key does not exist, False is returned.

        Raises:
        - TypeError: If the provided key is not of type int, str, or tuple.
        - ValueError: If the provided key is a string and starts with "~num~".

        Note:
        Before attempting to retrieve the value, the key is transformed using a private method `_transform_key_forward` to ensure it matches the format expected by the data store. This transformation is crucial for the accurate retrieval of data.
        """

        self._check_key_format_error(key)

        try:
            return self.db[self._transform_key_forward(key)]

        except KeyError:
            return False

    def rm(self, key: Union[int, float, str, list, tuple]) -> Any:
        """
        Removes a key-value pair from the data store and returns the value.

        This method attempts to remove a value associated with the given key from the data store.
        If the key exists, the key-value pair is removed, and the removed key and value is returned.
        If the key does not exist, the method returns False, indicating that no operation was performed for the given key.

        Parameters:
        - key (Union[int, float, str, list, tuple]): The key of the value to be removed. The key must be of type int, str, or tuple. If a key of a different type is provided, a TypeError will be raised.

        Returns:
        - Any: The removed key and value associated with the removed key from the data store. If the key does not exist, False is returned.

        Raises:
        - TypeError: If the provided key is not of type int, str, or tuple.
        - ValueError: If the provided key is a string and starts with "~num~".

        Note:
        The key is transformed using a private method `_transform_key_forward` before attempting the removal. This transformation ensures that the key conforms to the expected format of the data store's keys, facilitating accurate key lookup and removal.
        """

        self._check_key_format_error(key)

        try:
            popped_val = self.db.pop(self._transform_key_forward(key))
            self._auto_save()
            return (key, popped_val)

        except KeyError:
            return False

    def get_all_keys(self) -> list:
        """
        Retrieves a list of all the keys currently stored in the data store.

        This method provides a way to access all the keys in the data store, allowing for further operations such as iteration over keys, inspection of the data store's content, or performing bulk operations.
        The keys are returned in a list, reflecting their current state in the data store.

        Returns:
        - list: A list of all keys present in the data store. The type of the keys in the list will match the types of the keys when they were added to the store, which can include int, str, or tuple types, depending on the data store's usage.

        Note:
        The order of the keys in the returned list is not guaranteed and depends on the underlying data structure's ordering, which in most Python versions is insertion order for dictionaries.
        """
        l = self.db.keys()
        # apply transform backward to all elemets in the list to change them back to their original type
        return [self._transform_key_backward(x) for x in l]

    def get_all_values(self) -> list:
        """
        Retrieves all the values currently stored in the data store.

        This method compiles a list of all values from the data store, providing a snapshot of its content at the moment of invocation.
        It's useful for operations that require inspection or processing of every stored value.

        Returns:
        - list: A list containing every value stored in the data store. The types of the values can vary, reflecting the heterogeneous nature of the data stored, which can include but is not limited to, integers, strings, lists, dictionaries, or any other data type that has been added to the store.

        Note:
        The order of the values in the returned list is determined by the order of the corresponding keys in the data store. As such, this order may change when new key-value pairs are added or existing ones are removed. However, for most implementations of Python 3.7 and above, dictionaries maintain insertion order, which is likely to be reflected in the order of the returned values.
        """
        return list(self.db.values())

    def append(
        self, key: Union[int, float, str, list, tuple], val_to_append: Any
    ) -> Any:
        """
        Appends a value to an existing value in the data store.

        This method allows for the appending of a value to any value in the data store.
        If the key exists and the value is a list, the new value will be appended to the list.
        If the value is not a list , the method will make a list consisting of the existing value and append the new value to this new list.
        If the key does not exist, the method will return False.

        Parameters:
        - key (Union[int, float, str, list, tuple]): The key of the list to which the value is to be appended. The key must be of type int, str, or tuple. If a key of a different type is provided, a TypeError will be raised.
        - val (Any): The value to be appended to the list.

        Returns:
        - Any: The key and a list of values (old and new). If the key does not exist, False is returned.

        Raises:
        - TypeError: If the provided key is not of type int, str, or tuple.
        - ValueError: If the provided key is a string and starts with "~num~".

        Note:
        Before attempting to append the value, the key is transformed using a private method `_transform_key_forward` to ensure it matches the format expected by the data store. This transformation is crucial for the accurate retrieval of data.
        """

        self._check_key_format_error(key)

        try:
            vals = self.db[self._transform_key_forward(key)]
            vals = list(vals)
            vals.append(val_to_append)
            self.db[self._transform_key_forward(key)] = vals
            self._auto_save()
            return (key, vals)

        except KeyError:
            return False

    def add_to_str_or_num(
        self,
        key: Union[int, float, str, list, tuple],
        val_to_add: Union[int, float, str],
    ) -> Any:
        """
        Adds a value to an existing value in the data store only if the value associated with the given key is a int, float or a str.

        If the key exists and the value is an int, float or a str, the new value will be added to the int or float or new str will be appened to the existing str.
        If the value is not an int, float or a str, the method will return False.
        If there is a mismatch in the types of the existing value and the value to be added, the method will return False.
        If the key does not exist, the method will return False.

        Parameters:
        - key (Union[int, float, str, list, tuple]): The key of the int to which the value is to be added. The key must be of type int, str, or tuple. If a key of a different type is provided, a TypeError will be raised.
        - val_to_add (Union[int, float, str]): The value to be added to the value.

        Returns:
        - Any: The key and the new value. If the key does not exist or there is a mismatch in the types of value to be added and the existing value, False is returned.

        Raises:
        - TypeError: If the provided key is not of type int, str, or tuple.
        - ValueError: If the provided key is a string and starts with "~num~".

        Note:
        Before attempting to add the value, the key is transformed using a private method `_transform_key_forward` to ensure it matches the format expected by the data store. This transformation is crucial for the accurate retrieval of data.
        """

        self._check_key_format_error(key)

        try:
            key = self._transform_key_forward(key)
            val = self.db[key]

            if isinstance(val, (int, float)) and isinstance(val_to_add, (int, float)):
                self.db[key] = val + val_to_add
                self._auto_save()
                return (self._transform_key_backward(key), val + val_to_add)

            if isinstance(val, str) and isinstance(val_to_add, str):
                self.db[key] = val + val_to_add
                self._auto_save()
                return (self._transform_key_backward(key), val + val_to_add)

            return False

        except KeyError:
            return False

    def exists(self, key: Union[int, float, str, list, tuple]) -> bool:
        """
        Checks if a key exists in the data store.

        This method checks if a key exists in the data store.

        Parameters:
        - key (Union[int, float, str, list, tuple]): The key to be checked.

        Returns:
        - bool: True if the key exists in the data store, False otherwise.

        Raises:
        - TypeError: If the provided key is not of type int, str, or tuple.
        - ValueError: If the provided key is a string and starts with "~num~".

        Note:
        Before attempting to check the existence of the key, the key is transformed using a private method `_transform_key_forward` to ensure it matches the format expected by the data store. This transformation is crucial for the accurate retrieval of data.
        """

        self._check_key_format_error(key)

        return self._transform_key_forward(key) in self.db

    def totalkeys(self) -> int:
        """
        Returns the total number of keys in the data store.

        This method returns the total number of keys in the data store.

        Returns:
        - int: The total number of keys in the data store.
        """
        return len(self.db)

    def list_create(self, key: Union[int, float, str, list, tuple]) -> None:
        """
        Creates a list with the given key.

        This method creates a list with the given key.
        If the key already exists, the method will put the given value in a list.

        Parameters:
        - key (Union[int, float, str, list, tuple]): The key to be created.

        Returns:
        - None: The method does not return any value.

        Raises:
        - TypeError: If the provided key is not of type int, str, or tuple.
        - ValueError: If the provided key is a string and starts with "~num~".

        Note:
        Before attempting to create the list, the key is transformed using a private method `_transform_key_forward` to ensure it matches the format expected by the data store. This transformation is crucial for the accurate retrieval of data.
        """

        self._check_key_format_error(key)

        key = self._transform_key_forward(key)

        if key not in self.db:
            self.db[key] = []
        else:
            self.db[key] = [self.db[key]]

        self._auto_save()

    def list_add(self, key: Union[int, float, str, list, tuple], val: Any) -> Any:
        """
        Adds a value to a list in the data store.

        Calls the append method to add a value to a list in the data store.
        """

        self.append(key, val)

    def list_getall(self, key: Union[int, float, str, list, tuple]) -> Any:
        """
        Returns the values associated with a key as a list.

        If the key does not exist, the method will return False.

        Parameters:
        - key (Union[int, float, str, list, tuple]): The key for retrieval.

        Returns:
        - Any: The values associated with the key as a list. If the key does not exist, False is returned.

        Raises:
        - TypeError: If the provided key is not of type int, str, or tuple.
        - ValueError: If the provided key is a string and starts with "~num~".
        """

        self._check_key_format_error(key)

        try:
            return list(self.db[self._transform_key_forward(key)])

        except:
            return False

    def list_extend(
        self, key: Union[int, float, str, list, tuple], iterable_val: Iterable
    ) -> Any:
        """
        Extends the list with the given iterable sequence. Uses the Python extend method to achieve this.

        If the key does not exist or the given value is not an iterable, the method will return False.
        If the value associated with the key is not a list (including tuples), the value will be converted to a list with the existing value and then extended with the given iterable sequence.

        Parameters:
        - key (Union[int, float, str, list, tuple]): The key for retrieval.

        Returns:
        - Any: The key and the extended sequence of values associated with the key as a list. If the key does not exist, False is returned.

        Raises:
        - TypeError: If the provided key is not of type int, str, or tuple.
        - ValueError: If the provided key is a string and starts with "~num~".
        """

        self._check_key_format_error(key)

        if not isinstance(iterable_val, Iterable):
            return False

        try:
            val = list(self.db[self._transform_key_forward(key)])
            val.extend(iterable_val)
            self.db[self._transform_key_forward(key)] = val
            self._auto_save()
            return (key, val)

        except KeyError:
            return False

    def list_empty(self, key: Union[int, float, str, list, tuple]) -> Any:
        """
        Empties the list associated with the given key.

        If the key does not exist, the method will return False.
        If the value with the given key is not a list, the method will return False.

        Parameters:
        - key (Union[int, float, str, list, tuple]): The key for retrieval.

        Returns:
        - Any: Returns True if the operation is succesful. If the key does not exist or the value associated with the given key is not a list, False is returned.

        Raises:
        - TypeError: If the provided key is not of type int, str, or tuple.
        - ValueError: If the provided key is a string and starts with "~num~".
        """

        self._check_key_format_error(key)

        try:
            val = self.db[self._transform_key_forward(key)]

            if isinstance(val, list):
                self.db[self._transform_key_forward(key)] = []
                self._auto_save()
                return True

            return False

        except KeyError:
            return False


def load(location: str, auto_save: bool = False) -> KvickStore:
    """
    Loads a data store from a file. If the file does not exist, a new data store is created.

    Parameters:
    - location (str): The location of the file to be loaded.
    - auto_save (bool): If True, the data store will be saved automatically after every operation that modifies the data store. If False, the data store will not be saved automatically. The default value is False.

    Returns:
    - KvickStore: A KvickStore object that represents the data store loaded from the file.

    Raises:
    - ValueError: If the file exists but is empty or if the file exists but is not a valid JSON file.
    """

    return KvickStore(location, auto_save)
