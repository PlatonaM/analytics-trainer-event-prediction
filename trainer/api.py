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

__all__ = ("Model", )


from .logger import getLogger
from . import handlers
from . import model
import falcon
import json


logger = getLogger(__name__.split(".", 1)[-1])


def reqDebugLog(req):
    logger.debug("method='{}' path='{}' content_type='{}'".format(req.method, req.path, req.content_type))


def reqErrorLog(req, ex):
    logger.error("method='{}' path='{}' - {}".format(req.method, req.path, ex))


class Models:
    def __init__(self, stg_handler: handlers.Storage, conf_handler: handlers.Configs, jobs_handler: handlers.Jobs):
        self.__stg_handler = stg_handler
        self.__conf_handler = conf_handler
        self.__jobs_handler = jobs_handler

    def on_post(self, req: falcon.request.Request, resp: falcon.response.Response):
        reqDebugLog(req)
        try:
            model_req = model.ModelRequest(json.load(req.bounded_stream))
            model_resp = model.ModelResponse()
            model_resp.available = list()
            model_resp.pending = list()
            for m_id, m_conf in self.__conf_handler.get_model_id_config_list(service_id=model_req.service_id, config=model_req.ml_config):
                try:
                    self.__stg_handler.get(b"models-", m_id.encode())
                    model_resp.available.append(m_id)
                except KeyError:
                    self.__jobs_handler.create(service_id=model_req.service_id, model_id=m_id, config=m_conf)
                    model_resp.pending.append(m_id)
            resp.content_type = falcon.MEDIA_JSON
            resp.body = json.dumps(dict(model_resp))
            resp.status = falcon.HTTP_200
        except Exception as ex:
            resp.status = falcon.HTTP_500
            reqErrorLog(req, ex)


class Model:
    def __init__(self, stg_handler: handlers.Storage):
        self.__stg_handler = stg_handler

    def on_get(self, req: falcon.request.Request, resp: falcon.response.Response, model_id: str):
        reqDebugLog(req)
        try:
            resp.content_type = falcon.MEDIA_JSON
            resp.body = self.__stg_handler.get(b"models-", model_id.encode())
            resp.status = falcon.HTTP_200
        except KeyError as ex:
            resp.status = falcon.HTTP_404
            reqErrorLog(req, ex)
        except Exception as ex:
            resp.status = falcon.HTTP_500
            reqErrorLog(req, ex)

    # def on_put(self, req: falcon.request.Request, resp: falcon.response.Response, service_id: str):
    #     reqDebugLog(req)
    #     try:
    #         self.__stg_handler.put(service_id.encode(), req.bounded_stream.read())
    #         resp.status = falcon.HTTP_200
    #     except Exception as ex:
    #         resp.status = falcon.HTTP_500
    #         reqErrorLog(req, ex)

    # def on_delete(self, req: falcon.request.Request, resp: falcon.response.Response, service_id: str):
    #     reqDebugLog(req)
    #     try:
    #         self.__stg_handler.delete(service_id.encode())
    #         resp.status = falcon.HTTP_200
    #     except Exception as ex:
    #         resp.status = falcon.HTTP_500
    #         reqErrorLog(req, ex)


class Jobs:
    def __init__(self, jobs_handler: handlers.Jobs):
        self.__jobs_handler = jobs_handler

    def on_get(self, req: falcon.request.Request, resp: falcon.response.Response):
        reqDebugLog(req)
        try:
            resp.content_type = falcon.MEDIA_JSON
            resp.body = json.dumps(self.__jobs_handler.list_jobs())
            resp.status = falcon.HTTP_200
        except KeyError as ex:
            resp.status = falcon.HTTP_404
            reqErrorLog(req, ex)
        except Exception as ex:
            resp.status = falcon.HTTP_500
            reqErrorLog(req, ex)


class Job:
    def __init__(self, jobs_handler: handlers.Jobs):
        self.__jobs_handler = jobs_handler

    def on_get(self, req: falcon.request.Request, resp: falcon.response.Response, job_id):
        reqDebugLog(req)
        try:
            resp.content_type = falcon.MEDIA_JSON
            resp.body = json.dumps(dict(self.__jobs_handler.get_job(job_id)))
            resp.status = falcon.HTTP_200
        except KeyError as ex:
            resp.status = falcon.HTTP_404
            reqErrorLog(req, ex)
        except Exception as ex:
            resp.status = falcon.HTTP_500
            reqErrorLog(req, ex)
