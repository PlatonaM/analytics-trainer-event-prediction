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
from . import models
import falcon
import json


logger = getLogger(__name__.split(".", 1)[-1])


def reqDebugLog(req):
    logger.debug("method='{}' path='{}' content_type='{}'".format(req.method, req.path, req.content_type))


def reqErrorLog(req, ex):
    logger.error("method='{}' path='{}' - {}".format(req.method, req.path, ex))


class Models:
    def __init__(self, db_handler: handlers.DB, jobs_handler: handlers.Jobs):
        self.__db_handler = db_handler
        self.__jobs_handler = jobs_handler

    def on_get(self, req: falcon.request.Request, resp: falcon.response.Response):
        reqDebugLog(req)
        try:
            resp.content_type = falcon.MEDIA_JSON
            resp.body = json.dumps(self.__db_handler.list_keys(b"models-"))
            resp.status = falcon.HTTP_200
        except Exception as ex:
            resp.status = falcon.HTTP_500
            reqErrorLog(req, ex)

    def on_post(self, req: falcon.request.Request, resp: falcon.response.Response):
        reqDebugLog(req)
        try:
            model_req = models.ModelRequest(json.load(req.bounded_stream))
            model_resp = models.ModelResponse(available=list(), pending=list())
            for m_id, m_conf in handlers.configs.get_model_id_config_list(service_id=model_req.service_id, config=model_req.ml_config):
                try:
                    model = models.Model(json.loads(self.__db_handler.get(b"models-", m_id.encode())))
                    if model.data:
                        model_resp.available.append(m_id)
                    else:
                        model_resp.pending.append(m_id)
                except KeyError:
                    model = models.Model(service_id=model_req.service_id, id=m_id, config=m_conf)
                    self.__db_handler.put(b"models-", model.id.encode(), json.dumps(dict(model)).encode())
                    self.__jobs_handler.create(model_id=model.id)
                    model_resp.pending.append(m_id)
            resp.content_type = falcon.MEDIA_JSON
            resp.body = json.dumps(dict(model_resp))
            resp.status = falcon.HTTP_200
        except Exception as ex:
            resp.status = falcon.HTTP_500
            reqErrorLog(req, ex)


class Model:
    def __init__(self, db_handler: handlers.DB):
        self.__db_handler = db_handler

    def on_get(self, req: falcon.request.Request, resp: falcon.response.Response, model_id: str):
        reqDebugLog(req)
        try:
            resp.content_type = falcon.MEDIA_JSON
            resp.body = self.__db_handler.get(b"models-", model_id.encode())
            resp.status = falcon.HTTP_200
        except KeyError as ex:
            resp.status = falcon.HTTP_404
            reqErrorLog(req, ex)
        except Exception as ex:
            resp.status = falcon.HTTP_500
            reqErrorLog(req, ex)

    def on_delete(self, req: falcon.request.Request, resp: falcon.response.Response, model_id: str):
        reqDebugLog(req)
        try:
            self.__db_handler.delete(b"models-", model_id.encode())
            resp.status = falcon.HTTP_200
        except Exception as ex:
            resp.status = falcon.HTTP_500
            reqErrorLog(req, ex)


class Jobs:
    def __init__(self, db_handler: handlers.DB, jobs_handler: handlers.Jobs):
        self.__db_handler = db_handler
        self.__jobs_handler = jobs_handler

    def on_post(self, req: falcon.request.Request, resp: falcon.response.Response):
        reqDebugLog(req)
        try:
            req_body = json.load(req.bounded_stream)
            resp.body = self.__jobs_handler.create(req_body["model_id"])
            resp.content_type = falcon.MEDIA_TEXT
            resp.status = falcon.HTTP_200
        except Exception as ex:
            resp.status = falcon.HTTP_500
            reqErrorLog(req, ex)

    def on_get(self, req: falcon.request.Request, resp: falcon.response.Response):
        reqDebugLog(req)
        try:
            resp.content_type = falcon.MEDIA_JSON
            resp.body = json.dumps(
                dict(
                    current=self.__jobs_handler.list_jobs(),
                    history=self.__db_handler.list_keys(b"jobs-")
                )
            )
            resp.status = falcon.HTTP_200
        except Exception as ex:
            resp.status = falcon.HTTP_500
            reqErrorLog(req, ex)


class Job:
    def __init__(self, db_handler: handlers.DB, jobs_handler: handlers.Jobs):
        self.__db_handler = db_handler
        self.__jobs_handler = jobs_handler

    def on_get(self, req: falcon.request.Request, resp: falcon.response.Response, job_id):
        reqDebugLog(req)
        try:
            resp.content_type = falcon.MEDIA_JSON
            try:
                resp.body = json.dumps(dict(self.__jobs_handler.get_job(job_id)))
            except KeyError:
                resp.body = self.__db_handler.get(b"jobs-", job_id.encode())
            resp.status = falcon.HTTP_200
        except KeyError as ex:
            resp.status = falcon.HTTP_404
            reqErrorLog(req, ex)
        except Exception as ex:
            resp.status = falcon.HTTP_500
            reqErrorLog(req, ex)
