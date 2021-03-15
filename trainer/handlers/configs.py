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

__all__ = ("Configs", )


from ..logger import getLogger
from .. import model
import itertools
import hashlib


logger = getLogger(__name__.split(".", 1)[-1])


class Configs:
    def __init__(self, base_conf: dict, default_scaler: str, default_algorithm: str):
        self.__base_conf = base_conf
        self.__default_scaler = default_scaler
        self.__default_algorithm = default_algorithm

    def __configs_from_dict(self, config: dict) -> list:
        conf = self.__base_conf.copy()
        conf.update(config)
        if "scaler" not in conf:
            conf["scaler"] = [self.__default_scaler]
        if "ml_algorithm" not in conf:
            conf["ml_algorithm"] = [self.__default_algorithm]
        return [dict(zip(conf, v)) for v in itertools.product(*conf.values())]

    def __get_hash(self, service_id: str, config: dict) -> str:
        conf_ls = ["{}{}".format(key, val) for key, val in config.items()]
        conf_ls.sort()
        srv_conf_str = service_id + "".join(conf_ls)
        return hashlib.sha256(srv_conf_str.encode()).hexdigest()

    def get_model_id_config_list(self, service_id: str, config: dict) -> list:
        model_id_config_list = list()
        for config in self.__configs_from_dict(config):
            model_id_config_list.append((self.__get_hash(service_id=service_id, config=config), config))
        return model_id_config_list

