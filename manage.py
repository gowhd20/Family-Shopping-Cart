#!/Python27/python
from gevent.monkey import patch_all
patch_all()

import sys
sys.path.append(r'C:\Users\haejong\Desktop\mobile&social') 
from server.web_server import web_server
from flask import Flask

app = Flask(__name__)

app.register_blueprint(web_server,  url_prefix='/web_server')

from gevent.wsgi import WSGIServer
try:
    http_server = WSGIServer(("localhost", 1327), app)
    http_server.serve_forever()
except KeyboardInterrupt:
    print 'Exiting'