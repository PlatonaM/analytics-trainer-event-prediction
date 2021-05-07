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

__all__ = ("Data", )


from ..logger import getLogger
from .. import models
import requests
import json
import datetime
import uuid
import os
import time
import typing
import threading


logger = getLogger(__name__.split(".", 1)[-1])


def shift_year(timestamp: str, year_map: dict):
    year = timestamp.split("-", 1)[0]
    return timestamp.replace(year, year_map[year])


def gen_year_map(start: int, end: int, base: int):
    map = dict()
    for x in range(end - start + 1):
        map[str(start + x)] = str(base + x)
    return map


class CacheItem:
    def __init__(self):
        self.file_name = None
        self.columns = None
        self.default_values = None
        self.last_accessed = None
        self.lock = threading.Lock()


class Data(threading.Thread):
    def __init__(self, st_path: str, db_api_url: str, export_api_url: str, time_format: str, db_api_time_format: str, start_year: int, chunk_size: int, usr_id: str, max_age: int):
        super().__init__(name="data-handler", daemon=True)
        self.__st_path = st_path
        self.__db_api_url = db_api_url
        self.__export_api_url = export_api_url
        self.__time_format = time_format
        self.__db_api_time_format = db_api_time_format
        self.__start_year = start_year
        self.__chunk_size = chunk_size
        self.__usr_id = usr_id
        self.__max_age = max_age
        self.__cache: typing.Dict[str, CacheItem] = dict()
        self.__lock = threading.Lock()

    def __get_data(self, measurement: str, sort: str, **kwargs):
        kwargs["measurement"] = measurement
        kwargs["columns"] = [{"name": "data"}, {"name": "default_values"}]
        resp = requests.post(
            url="{}?format=table&order_direction={}&order_column_index=0&time_format={}".format(
                self.__db_api_url,
                sort,
                self.__db_api_time_format
            ),
            headers={"X-UserId": self.__usr_id},
            json=[kwargs]
        )
        if not resp.ok:
            raise RuntimeError(resp.status_code)
        return resp.json()

    def __get_start_timestamp(self, measurement: str) -> str:
        return self.__get_data(measurement=measurement, sort="asc", limit=1)[0][0]

    def __get_end_timestamp(self, measurement: str) -> str:
        return self.__get_data(measurement=measurement, sort="desc", limit=1)[0][0]

    def __get_chunks(self, measurement: str, start: str, end: str):
        start = datetime.datetime.strptime(start, self.__time_format) - datetime.timedelta(microseconds=1)
        start = start.isoformat() + "Z"
        end = datetime.datetime.strptime(end, self.__time_format) + datetime.timedelta(microseconds=1)
        end = end.isoformat() + "Z"
        while True:
            chunk = self.__get_data(measurement=measurement, sort="asc", limit=self.__chunk_size, time={"start": start, "end": end})
            if not chunk:
                break
            else:
                logger.debug(
                    "retrieved chunk with size of '{}' from '{}' - '{}' for '{}'".format(len(chunk), start, end, measurement)
                )
                start = chunk[-1][0]
                yield chunk

    def __get_source_ids(self, srv_id: str):
        resp = requests.get(
            url=self.__export_api_url,
            headers={"X-UserId": self.__usr_id}
        )
        if not resp.ok:
            raise RuntimeError(resp.status_code)
        resp = resp.json()
        src_ids = set()
        for item in resp["instances"]:
            if item["Description"] == srv_id:
                logger.debug("found '{}' for '{}'".format(item["Measurement"], srv_id))
                src_ids.add(item["Measurement"])
        return src_ids

    def __get(self, srv_id: str, time_field: str, delimiter: str):
        try:
            sources = list()
            start_year = self.__start_year
            for src_id in sorted(self.__get_source_ids(srv_id)):
                source = models.DataSource()
                source.id = src_id
                source.start = self.__get_start_timestamp(measurement=src_id)
                source.end = self.__get_end_timestamp(measurement=src_id)
                source.year_map = gen_year_map(
                    start=int(source.start.split("-", 1)[0]),
                    end=int(source.end.split("-", 1)[0]),
                    base=start_year
                )
                start_year = start_year + len(source.year_map)
                sources.append(source)
            chunks = list()
            header = set()
            default_values = dict()
            for source in sources:
                for chunk in self.__get_chunks(measurement=source.id, start=source.start, end=source.end):
                    chunk_name = uuid.uuid4().hex
                    chunks.append(chunk_name)
                    with open(os.path.join(self.__st_path, chunk_name), "w") as file:
                        for item in chunk:
                            data: dict = json.loads(item[1])
                            data[time_field] = shift_year(item[0], source.year_map)
                            header.update(data.keys())
                            default_values.update(json.loads(item[2]))
                            file.write(json.dumps(data, separators=(',', ':')) + "\n")
            header.discard(time_field)
            header = [time_field, *sorted(header)]
            line_map = dict()
            for x in range(len(header)):
                line_map[x] = header[x]
            file_name = uuid.uuid4().hex
            with open(os.path.join(self.__st_path, file_name), "w") as file:
                file.write(delimiter.join(header) + "\n")
                _range = range(len(header))
                for chunk in chunks:
                    with open(os.path.join(self.__st_path, chunk), "r") as chunk_file:
                        for line in chunk_file:
                            line = json.loads(line.strip())
                            _line = list()
                            for x in _range:
                                try:
                                    value = str(line[line_map[x]])
                                except KeyError:
                                    try:
                                        value = str(default_values[line_map[x]])
                                    except KeyError:
                                        value = str()
                                _line.append(value)
                            file.write(delimiter.join(_line) + "\n")
            for chunk in chunks:
                try:
                    os.remove(os.path.join(self.__st_path, chunk))
                except Exception:
                    pass
            return file_name, header, default_values
        except Exception as ex:
            logger.error("could not get data for '{}' - {}".format(srv_id, ex))
            raise ex

    def get(self, srv_id: str, time_field: str, delimiter: str) -> typing.Tuple[str, list, dict]:
        with self.__lock:
            if srv_id not in self.__cache:
                self.__cache[srv_id] = CacheItem()
        cache_item = self.__cache[srv_id]
        with cache_item.lock:
            if not cache_item.file_name:
                cache_item.file_name, cache_item.columns, cache_item.default_values = self.__get(
                    srv_id=srv_id,
                    time_field=time_field,
                    delimiter=delimiter
                )
            cache_item.last_accessed = time.time()
            return cache_item.file_name, cache_item.columns, cache_item.default_values

    def run(self) -> None:
        stale_items = list()
        while True:
            time.sleep(self.__max_age / 2)
            with self.__lock:
                for key, item in self.__cache.items():
                    if time.time() - item.last_accessed > self.__max_age and not item.lock.locked():
                        stale_items.append(key)
                for key in stale_items:
                    try:
                        os.remove(os.path.join(self.__st_path, self.__cache[key].file_name))
                    except Exception:
                        pass
                    del self.__cache[key]
            stale_items.clear()
