from gevent import monkey

from main import create_app

monkey.patch_all()

from gevent.pywsgi import WSGIServer

http_server = WSGIServer(("0.0.0.0", 5556), create_app())
http_server.serve_forever()
