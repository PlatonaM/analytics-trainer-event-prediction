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


import simple_struct


__all__ = ("Job", "JobStatus", "Model", "ModelResponse", "ModelRequest", "MetaData")


class JobStatus:
    pending = "pending"
    running = "running"
    finished = "finished"
    failed = "failed"
    aborted = "aborted"


@simple_struct.structure
class Job:
    id = None
    created = None
    status = JobStatus.pending
    model_id = None
    reason = None


@simple_struct.structure
class Model:
    id = None
    created = None
    config = None
    columns = None
    data = None
    default_values = None
    service_id = None
    time_field = None


@simple_struct.structure
class ModelRequest:
    service_id = None
    ml_config = None
    # time_field = None


@simple_struct.structure
class ModelResponse:
    available = None
    pending = None


@simple_struct.structure
class MetaData:
    source_id: str = None
    time_field: str = None
    delimiter: str = None
    # sources: dict = None
    # size: int = 0
    created: str = None
    columns: list = None
    default_values: dict = None
    files: list = None
    checksum = None
    compressed = None
