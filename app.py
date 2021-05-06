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


initLogger(conf.Logger.level)

data_handler = handlers.Data(api_url=conf.Data.api_url)
stg_handler = handlers.Storage(st_path=conf.Storage.db_path)
jobs_handler = handlers.Jobs(
    stg_handler=stg_handler,
    data_handler=data_handler,
    check_delay=conf.Jobs.check,
    max_jobs=conf.Jobs.max_num
)
skd_handler = handlers.Scheduler(job_handler=jobs_handler, stg_handler=stg_handler, delay=conf.Jobs.skd_delay)

app = falcon.API()

app.req_options.strip_url_path_trailing_slash = True

routes = (
    ("/models", api.Models(stg_handler=stg_handler, jobs_handler=jobs_handler)),
    ("/models/{model_id}", api.Model(stg_handler=stg_handler)),
    ("/jobs", api.Jobs(stg_handler=stg_handler, jobs_handler=jobs_handler)),
    ("/jobs/{job_id}", api.Job(stg_handler=stg_handler, jobs_handler=jobs_handler))
)

for route in routes:
    app.add_route(*route)

jobs_handler.start()
skd_handler.start()
