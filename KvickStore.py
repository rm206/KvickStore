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

    def _tranformkey(self, key: Union[int, tuple]) -> str:
        """
        Function to transform the key to a string for JSON serialization
        """
        if isinstance(key, tuple):
            return str(key)
        if isinstance(key, int):
            return "int" + str(key)
        return key

    def set(self, key: Union[int, str, tuple], val: Any) -> Any:
        if not isinstance(key, (int, str, tuple)):
            raise self.type_error

        key = self._tranformkey(key)
        self.db[key] = val

    def get(self, key: Union[int, str, tuple]) -> Any:
        if not isinstance(key, (int, str, tuple)):
            raise self.type_error

        key = self._tranformkey(key)
        try:
            return self.db[key]
        except KeyError:
            return False

    def remov(self, key: Union[int, str, tuple]) -> Any:
        if not isinstance(key, (int, str, tuple)):
            raise self.type_error

        key = self._tranformkey(key)
        try:
            return self.db.pop(key)
        except KeyError:
            return False

    def get_all_keys(self) -> list:
        """
        Returns all the keys in the store
        """
        return self.db.keys()

    def get_all_values(self) -> list:
        """
        Returns all the values in the store
        """
        return self.db.values()
