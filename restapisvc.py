# coding=utf-8

"""
RESTful API Service version: v0.1.1
WUCHENG     May 17, 2019

version history:
v0.1.1 May 17, 2019     first version
example:
import restapisvc

def myhandler(aJson):
    print(aJson)
    return {'a':5}

restapisvc.RPC_Service(json_handler=myhandler, port=22222).run()
# shell cmd ----  curl -d '{"a":"aaaaa", "b":3, "c":true}' http://127.0.0.1:22222

"""

from aiohttp import web
import ssl
import json
import logging

class RPC_Service(object):
    def __init__(self, port, json_handler, host=None, https=False, log_data=False):
        self.logger = logging.getLogger('restapisvc')
        self.log_data = log_data
        
        self.port = port
        self.host = host
        self.json_handler = json_handler

        self.app = web.Application()
        
        if https:
            self.ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        else:
            self.ssl_context = None
            
    def run(self):
        self.app.router.add_post('/', self.handler)
        web.run_app(self.app, host=self.host, port=self.port, ssl_context=self.ssl_context)

    async def handler(self, request):
        response_400 = { 'status' : '400 Bad Request' }
        json_response = {}

        if request.body_exists:
            json_request = await request.json()
        else:
            return web.Response(text=json.dumps(response_400), status=400, content_type='application/json')

        if json_request:
            if self.log_data:
                self.logger.info('Got request json: %s' % json.dumps(json_request))
                
            json_response = self.json_handler(json_request)
        else:
            return web.Response(text=json.dumps(response_400), status=400, content_type='application/json')
            
        if self.log_data:
            self.logger.info('Response json: %s' % json.dumps(json_response))
        return web.Response(text=json.dumps(json_response), status=200, content_type='application/json')
