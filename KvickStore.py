from typing import Union, Any


class KvickStore:
    def __init__(self):
        self.db = {}
        self.type_error = TypeError("Key must be of type int, str or tuple")

    def __setitem__(self, key: Union[int, str, tuple], val: Any) -> Any:
        """
        Allows the use of the [] operator to set a value
        """
        self.set(key, val)

    def __getitem__(self, key: Union[int, str, tuple]) -> Any:
        """
        Allows the use of the [] operator to get a value
        """
        return self.get(key)

    def __delitem__(self, key: Union[int, str, tuple]) -> Any:
        """
        Allows the use of the del operator to remove a key-value pair
        """
        return self.rm(key)

    def _transform_key_forward(self, key: Union[int, tuple]) -> str:
        """
        Internal function to transform the key to a string for JSON serialization
        """
        if isinstance(key, tuple):
            return str(key)
        if isinstance(key, int):
            return "int" + str(key)
        return key

    def _transform_key_backward(self, key: str) -> Union[int, str, tuple]:
        """
        Internal function to transform the key back to its original type
        """
        if key.startswith("int"):
            return int(key[3:])
        if key.startswith("("):
            return tuple(key[1:-1].split(", "))
        return key

    def set(self, key: Union[int, str, tuple], val: Any) -> Any:
        """
        Sets a value in the data store.

        This method assigns a given value to a specified key within the data store. If the key already exists, the existing value will be overwritten with the new value.

        Parameters:
        - key (Union[int, str, tuple]): The key under which the value is stored. The key must be of type int, str, or tuple. If a key of a different type is provided, a TypeError will be raised.
        - val (Any): The value to be stored in the data store.

        Returns:
        - Any: The value that was set in the data store.

        Raises:
        - TypeError: If the provided key is not of type int, str, or tuple.

        Note:
        Tuples when stored as values will be converted to lists. When retrieved, the value will be a list. This is due to the fact that JSON does not support the storage of tuples.
        Due to JSON limitations, if a dictionary is stored as a value, trying to have non-string keys will raise a TypeError.
        The method internally transforms the key using a private method `_transform_key_forward` before storing the value in the database. This transformation is applied to ensure the key conforms to the storage requirements of the data store.
        """
        if not isinstance(key, (int, str, tuple)):
            raise self.type_error

        key = self._transform_key_forward(key)
        self.db[key] = val

    def get(self, key: Union[int, str, tuple]) -> Any:
        """
        Retrieves a value from the data store based on the given key.

        This method looks up a value in the data store using the specified key. If the key exists, the corresponding value is returned. If the key does not exist, the method returns False, indicating the absence of a value for the given key.

        Parameters:
        - key (Union[int, str, tuple]): The key for which the value is to be retrieved. The key must be of type int, str, or tuple. If a key of a different type is provided, a TypeError will be raised.

        Returns:
        - Any: The value associated with the given key in the data store. If the key does not exist, False is returned.

        Raises:
        - TypeError: If the provided key is not of type int, str, or tuple.

        Note:
        Before attempting to retrieve the value, the key is transformed using a private method `_transform_key_forward` to ensure it matches the format expected by the data store. This transformation is crucial for the accurate retrieval of data.
        """
        if not isinstance(key, (int, str, tuple)):
            raise self.type_error

        key = self._transform_key_forward(key)
        try:
            return self.db[key]
        except KeyError:
            return False

    def rm(self, key: Union[int, str, tuple]) -> Any:
        """
        Removes a key-value pair from the data store and returns the value.

        This method attempts to remove a value associated with the given key from the data store. If the key exists, the key-value pair is removed, and the value is returned. If the key does not exist, the method returns False, indicating that no operation was performed for the given key.

        Parameters:
        - key (Union[int, str, tuple]): The key of the value to be removed. The key must be of type int, str, or tuple. If a key of a different type is provided, a TypeError will be raised.

        Returns:
        - Any: The value associated with the removed key from the data store. If the key does not exist, False is returned.

        Raises:
        - TypeError: If the provided key is not of type int, str, or tuple.

        Note:
        The key is transformed using a private method `_transform_key_forward` before attempting the removal. This transformation ensures that the key conforms to the expected format of the data store's keys, facilitating accurate key lookup and removal.
        """
        if not isinstance(key, (int, str, tuple)):
            raise self.type_error

        key = self._transform_key_forward(key)
        try:
            return self.db.pop(key)
        except KeyError:
            return False

    def get_all_keys(self) -> list:
        """
        Retrieves a list of all the keys currently stored in the data store.

        This method provides a way to access all the keys in the data store, allowing for further operations such as iteration over keys, inspection of the data store's content, or performing bulk operations. The keys are returned in a list, reflecting their current state in the data store.

        Returns:
        - list: A list of all keys present in the data store. The type of the keys in the list will match the types of the keys when they were added to the store, which can include int, str, or tuple types, depending on the data store's usage.

        Note:
        The order of the keys in the returned list is not guaranteed and depends on the underlying data structure's ordering, which in most Python versions is insertion order for dictionaries.
        """
        l = list(self.db.keys())
        # apply transform backward to all elemets in the list to change them back to their original type
        return [self._transform_key_backward(x) for x in l]

    def get_all_values(self) -> list:
        """
        Retrieves all the values currently stored in the data store.

        This method compiles a list of all values from the data store, providing a snapshot of its content at the moment of invocation. It's useful for operations that require inspection or processing of every stored value.

        Returns:
        - list: A list containing every value stored in the data store. The types of the values can vary, reflecting the heterogeneous nature of the data stored, which can include but is not limited to, integers, strings, lists, dictionaries, or any other data type that has been added to the store.

        Note:
        The order of the values in the returned list is determined by the order of the corresponding keys in the data store. As such, this order may change when new key-value pairs are added or existing ones are removed. However, for most implementations of Python 3.7 and above, dictionaries maintain insertion order, which is likely to be reflected in the order of the returned values.
        """
        return list(self.db.values())
