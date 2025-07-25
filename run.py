import os
from wsgiref.simple_server import make_server

def app(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return [b'FoodXchange is running!']

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    server = make_server('0.0.0.0', port, app)
    print(f'Serving on port {port}')
    server.serve_forever()