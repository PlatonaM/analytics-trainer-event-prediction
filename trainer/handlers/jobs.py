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

__all__ = ("Jobs",)


from ..logger import getLogger
from .. import model
from . import Storage
import threading
import queue
import typing
import time
import uuid
import datetime
import base64
import gzip
import json
import time


logger = getLogger(__name__.split(".", 1)[-1])


class Worker(threading.Thread):
    def __init__(self, job: model.Job, stg_handler: Storage):
        super().__init__(name="jobs-worker-{}".format(job.id), daemon=True)
        self.__stg_handler = stg_handler
        self.__job = job
        self.done = False

    def run(self) -> None:
        try:
            logger.debug("starting job '{}' ...".format(self.__job.id))
            self.__job.status = model.JobStatus.running
            time.sleep(20)
            with open("out_comp", "r") as file:
                data = file.read()
            _model = model.Model()
            _model.id = self.__job.model_id
            _model.columns = ['time', 'location_ec-generator_gesamtwirkleistung', 'location_ec-gesamt_gesamtwirkleistung', 'location_ec-prozess_gesamtwirkleistung', 'location_ec-roboter_gesamtwirkleistung', 'location_roboter-ausgabe_gesamtwirkleistung', 'location_roboter-eingabe_gesamtwirkleistung', 'location_transport-gesamt_gesamtwirkleistung', 'location_wm1-gesamt_gesamtwirkleistung', 'location_wm1-heizung-reinigen_gesamtwirkleistung', 'location_wm1-heizung-trocknung_gesamtwirkleistung', 'location_wm2-gesamt_gesamtwirkleistung', 'location_wm2-heizung-reinigen_gesamtwirkleistung', 'location_wm2-heizung-trocknung_gesamtwirkleistung', 'location_wm2-vakuumpumpe_gesamtwirkleistung', 'module_1_errorcode', 'module_1_errorindex', 'module_1_state', 'module_1_station_1_process_1_errorcode_0', 'module_1_station_2_process_1_errorcode_0', 'module_1_station_31_process_1_errorcode_0', 'module_1_station_31_process_1_errorcode_998', 'module_1_station_3_process_1_errorcode_0', 'module_1_station_4_process_1_errorcode_0', 'module_1_station_5_process_1_errorcode_0', 'module_1_station_6_process_1_errorcode_0', 'module_2_errorcode', 'module_2_errorindex', 'module_2_state', 'module_2_station_1_process_1_errorcode_0', 'module_2_station_21_process_1_errorcode_999', 'module_2_station_22_process_1_errorcode_0', 'module_2_station_24_process_1_errorcode_0', 'module_2_station_25_process_1_errorcode_51', 'module_2_station_25_process_1_errorcode_55', 'module_2_station_28_process_1_errorcode_51', 'module_2_station_28_process_1_errorcode_55', 'module_2_station_28_process_1_errorcode_980', 'module_2_station_3_process_1_errorcode_0', 'module_2_station_3_process_1_errorcode_998', 'module_2_station_4_process_1_errorcode_0', 'module_2_station_4_process_1_errorcode_998', 'module_2_station_50_process_1_errorcode_0', 'module_2_station_51_process_1_errorcode_0', 'module_2_station_51_process_1_errorcode_51', 'module_2_station_51_process_1_errorcode_55', 'module_2_station_5_process_1_errorcode_0', 'module_2_station_5_process_1_errorcode_998', 'module_2_station_6_process_1_errorcode_0', 'module_2_station_6_process_1_errorcode_998', 'module_4_errorcode', 'module_4_errorindex', 'module_4_state', 'module_5_errorcode', 'module_5_errorindex', 'module_5_state', 'module_6_errorcode', 'module_6_errorindex', 'module_6_state']
            _model.config = self.__job.config
            _model.data = data
            _model.created = '{}Z'.format(datetime.datetime.utcnow().isoformat())
            self.__stg_handler.put(b"models-", _model.id.encode(), json.dumps(dict(_model)).encode())
            self.__job.status = model.JobStatus.finished
        except Exception as ex:
            self.__job.status = model.JobStatus.failed
            self.__job.reason = str(ex)
            logger.error("{}: failed - {}".format(self.__job.id, ex))
        self.done = True


class Jobs(threading.Thread):
    def __init__(self, stg_handler: Storage, check_delay: typing.Union[int, float], max_jobs: int):
        super().__init__(name="jobs-handler", daemon=True)
        self.__stg_handler = stg_handler
        self.__check_delay = check_delay
        self.__max_jobs = max_jobs
        self.__job_queue = queue.Queue()
        self.__job_pool: typing.Dict[str, model.Job] = dict()
        self.__worker_pool: typing.Dict[str, Worker] = dict()

    def create(self, service_id: str, model_id: str, config: dict) -> str:
        for job in self.__job_pool.values():
            if job.model_id == model_id:
                return job.id
        job = model.Job()
        job.id = uuid.uuid4().hex
        job.service_id = service_id
        job.model_id = model_id
        job.config = config
        job.created = '{}Z'.format(datetime.datetime.utcnow().isoformat())
        self.__job_pool[job.id] = job
        self.__job_queue.put_nowait(job.id)
        # self.__stg_handler.put(b"jobs-", job_id.encode(), json.dumps(self.__job_pool[job_id]).encode())
        return job.id

    def get_job(self, job_id: str) -> model.Job:
        return self.__job_pool[job_id]

    def list_jobs(self) -> list:
        return list(self.__job_pool.keys())

    def run(self):
        while True:
            if len(self.__worker_pool) < self.__max_jobs:
                try:
                    job_id = self.__job_queue.get(timeout=self.__check_delay)
                    worker = Worker(job=self.__job_pool[job_id], stg_handler=self.__stg_handler)
                    self.__worker_pool[job_id] = worker
                    worker.start()
                except queue.Empty:
                    pass
            else:
                time.sleep(self.__check_delay)
            for job_id in list(self.__worker_pool.keys()):
                if self.__worker_pool[job_id].done:
                    del self.__worker_pool[job_id]
                    del self.__job_pool[job_id]
                    # self.__stg_handler.delete(b"jobs-", job_id)
