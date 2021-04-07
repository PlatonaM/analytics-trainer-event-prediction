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

__all__ = ("get_model_id_config_list", )


from ..logger import getLogger
from .. import event_prediction_trainer
import hashlib


logger = getLogger(__name__.split(".", 1)[-1])


def __get_hash(service_id: str, source_id: str, config: dict) -> str:
    conf_ls = ["{}{}".format(key, val) for key, val in config.items()]
    conf_ls.sort()
    srv_conf_str = service_id + source_id + "".join(conf_ls)
    return hashlib.sha256(srv_conf_str.encode()).hexdigest()


def get_model_id_config_list(service_id: str, source_id: str, config: dict) -> list:
    model_id_config_list = list()
    for _config in event_prediction_trainer.config.configs_from_dict(config=config, init=False):
        model_id_config_list.append((__get_hash(service_id=service_id, source_id=source_id, config=_config), _config))
    return model_id_config_list
