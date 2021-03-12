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

from trainer.logger import initLogger
from trainer.configuration import conf
from trainer import handlers
from trainer import api
import falcon
import json


initLogger(conf.Logger.level)

stg_handler = handlers.Storage(st_path=conf.Storage.path)
configs_handler = handlers.Configs(
    base_conf=json.loads(conf.MLConfig.base_conf),
    default_scaler=conf.MLConfig.default_scaler,
    default_algorithm=conf.MLConfig.default_algorithm
)
jobs_handler = handlers.Jobs(stg_handler=stg_handler, check_delay=conf.Jobs.check, max_jobs=conf.Jobs.max_num)

app = falcon.API()

app.req_options.strip_url_path_trailing_slash = True

routes = (
    ("/models", api.Models(stg_handler=stg_handler, conf_handler=configs_handler, jobs_handler=jobs_handler)),
    ("/models/{model_id}", api.Model(stg_handler=stg_handler)),
    ("/jobs", api.Jobs(jobs_handler=jobs_handler)),
    ("/jobs/{job_id}", api.Job(jobs_handler=jobs_handler))
)

for route in routes:
    app.add_route(*route)

jobs_handler.start()
