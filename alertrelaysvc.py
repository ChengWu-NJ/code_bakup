# coding=utf-8

"""
alert relay service with http event version: v0.1.1
WUCHENG     May 17, 2019

version history:
v0.1.1 May 17, 2019     first version

"""

from aiohttp import web
import socketio
import ssl
import json
import logging

class Alert_relay(object):
    def __init__(self, port, host=None, https=False, log_data=False, event_page='alert.html'):
        self.logger = logging.getLogger('restapisvc')
        self.log_data = log_data
        
        self.port = port
        self.host = host

        self.app = web.Application()
        self.sio = socketio.AsyncServer()
        self.sio.attach(self.app)
        self.event_page = event_page
        
        if https:
            self.ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        else:
            self.ssl_context = None
            
            
    def run(self):
        self.app.router.add_get('/', self.wp_handler)
        self.app.router.add_get('/'+self.event_page, self.wp_handler)
        self.app.router.add_get('/socket.io.js', self.wp_handler)
        self.app.router.add_post('/', self.handler)
        web.run_app(self.app, host=self.host, port=self.port, ssl_context=self.ssl_context)

 
    async def wp_handler(self, request):
        print(request.path_qs)
        if request.path_qs == '/' or request.path_qs == '/'+self.event_page:
            resp = web.FileResponse(self.event_page)
        
        if request.path_qs == '/socket.io.js':
            resp = web.FileResponse('socket.io.js')
        return resp
    
    
    async def handler(self, request):
        response_400 = { 'status' : '400 Bad Request' }
        response_200 = { 'status' : '200 Ok' }

        if request.body_exists:
            json_request = await request.json()
        else:
            return web.Response(text=json.dumps(response_400), status=400, content_type='application/json')

        if json_request:
            if self.log_data:
                self.logger.info('Got request json: %s' % json.dumps(json_request))

            await self.sio.emit('alertEvent', json.dumps(json_request))
        else:
            return web.Response(text=json.dumps(response_400), status=400, content_type='application/json')
            
        return web.Response(text=json.dumps(response_200), status=200, content_type='application/json')

    
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    Alert_relay(53421, log_data=True).run()
    
