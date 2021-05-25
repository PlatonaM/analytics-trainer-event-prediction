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
from .. import event_prediction_trainer
from .. import models
from . import DB, Data
import threading
import queue
import typing
import uuid
import datetime
import base64
import gzip
import json
import time


logger = getLogger(__name__.split(".", 1)[-1])


class Worker(threading.Thread):
    def __init__(self, job: models.Job, db_handler: DB, data_handler: Data):
        super().__init__(name="jobs-worker-{}".format(job.id), daemon=True)
        self.__db_handler = db_handler
        self.__data_handler = data_handler
        self.__job = job
        self.done = False

    def run(self) -> None:
        try:
            logger.debug("starting job '{}' ...".format(self.__job.id))
            self.__job.status = models.JobStatus.running
            model = models.Model(json.loads(self.__db_handler.get(b"models-", self.__job.model_id.encode())))
            config = event_prediction_trainer.config.config_from_dict(model.config)
            file_path, model.columns, model.default_values, model.time_field = self.__data_handler.get(source_id=model.service_id)
            logger.debug(
                "{}: training model for prediction of '{}' for '{}' ...".format(
                    self.__job.id, config["target_errorCode"],
                    config["target_col"]
                )
            )
            model.data = base64.standard_b64encode(
                gzip.compress(
                    event_prediction_trainer.pipeline.clf_to_pickle_bytes(
                        event_prediction_trainer.pipeline.run_pipeline(
                            df=event_prediction_trainer.pipeline.df_from_csv(
                                csv_path=file_path,
                                time_col=model.time_field,
                                sorted=True
                            ),
                            config=config
                        )
                    )
                )
            ).decode()
            model.created = "{}Z".format(datetime.datetime.utcnow().isoformat())
            self.__db_handler.put(b"models-", model.id.encode(), json.dumps(dict(model)).encode())
            self.__job.status = models.JobStatus.finished
            logger.debug("{}: completed successfully".format(self.__job.id))
        except Exception as ex:
            self.__job.status = models.JobStatus.failed
            self.__job.reason = str(ex)
            logger.error("{}: failed - {}".format(self.__job.id, ex))
        self.__db_handler.put(b"jobs-", self.__job.id.encode(), json.dumps(dict(self.__job)).encode())
        self.done = True


class Jobs(threading.Thread):
    def __init__(self, db_handler: DB, data_handler: Data, check_delay: typing.Union[int, float], max_jobs: int):
        super().__init__(name="jobs-handler", daemon=True)
        self.__db_handler = db_handler
        self.__data_handler = data_handler
        self.__check_delay = check_delay
        self.__max_jobs = max_jobs
        self.__job_queue = queue.Queue()
        self.__job_pool: typing.Dict[str, models.Job] = dict()
        self.__worker_pool: typing.Dict[str, Worker] = dict()

    def create(self, model_id: str) -> str:
        for job in self.__job_pool.values():
            if job.model_id == model_id:
                logger.debug("job for model '{}' already exists".format(model_id))
                return job.id
        job = models.Job(
            id=uuid.uuid4().hex,
            model_id=model_id,
            created="{}Z".format(datetime.datetime.utcnow().isoformat())
        )
        self.__job_pool[job.id] = job
        logger.debug("created job for model '{}'".format(model_id))
        self.__job_queue.put_nowait(job.id)
        return job.id

    def get_job(self, job_id: str) -> models.Job:
        return self.__job_pool[job_id]

    def list_jobs(self) -> list:
        return list(self.__job_pool.keys())

    def run(self):
        while True:
            if len(self.__worker_pool) < self.__max_jobs:
                try:
                    job_id = self.__job_queue.get(timeout=self.__check_delay)
                    worker = Worker(
                        job=self.__job_pool[job_id],
                        db_handler=self.__db_handler,
                        data_handler=self.__data_handler
                    )
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
                    # self.__db_handler.delete(b"jobs-", job_id.encode())
