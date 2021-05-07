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

stg_handler = handlers.Storage(st_path=conf.Storage.db_path)
data_handler = handlers.Data(
    st_path=conf.Storage.data_cache_path,
    db_api_url=conf.CacheItem.db_api_url,
    export_api_url=conf.CacheItem.export_api_url,
    time_format=conf.CacheItem.time_format,
    db_api_time_format=conf.CacheItem.db_api_time_format,
    start_year=conf.CacheItem.start_year,
    chunk_size=conf.CacheItem.chunk_size,
    usr_id=conf.CacheItem.usr_id,
    max_age=conf.CacheItem.max_age
)
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
data_handler.start()
