from gevent.pywsgi import WSGIServer
from web.main import app

http_server = WSGIServer(('', 18513), app)
http_server.serve_forever()