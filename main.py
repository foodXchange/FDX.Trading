#!/usr/bin/env python
"""Absolute minimal Python web server"""
import os

def app(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return [b'FoodXchange is running on Azure!']

application = app

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    port = int(os.environ.get('PORT', 8000))
    server = make_server('', port, application)
    print(f'Serving on port {port}')
    server.serve_forever()