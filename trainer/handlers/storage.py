"""
   Copyright 2021 InfAI (CC SES)

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

__all__ = ("Storage", )


from ..logger import getLogger
import plyvel

logger = getLogger(__name__.split(".", 1)[-1])


class Storage:
    def __init__(self, st_path):
        self.__kvs = plyvel.DB(st_path, create_if_missing=True)

    def put(self, key: bytes, value: bytes):
        self.__kvs.put(key, value)

    def get(self, key: bytes) -> bytes:
        value = self.__kvs.get(key)
        if not value:
            raise KeyError(key)
        return value

    def delete(self, key: bytes):
        self.__kvs.delete(key)

    def close(self):
        self.__kvs.close()