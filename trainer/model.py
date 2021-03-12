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


__all__ = ("Job", "JobStatus")


class JobStatus:
    pending = "pending"
    running = "running"
    finished = "finished"
    failed = "failed"
    aborted = "aborted"


class Job:
    id = "id"
    created = "created"
    status = "status"
    model_id = "model_id"
    config = "config"
    service_id = "service_id"
    reason = "reason"
    time_field = "time_field"
    sorted_data = "sorted_data"


class Model:
    id = "id"
    created = "created"
    data = "data"
    columns = "columns"


class ModelRequest:
    service_id = "service_id"
    ml_config = "ml_config"


class ModelResponse:
    model_id = "model_id"
    config = "config"
