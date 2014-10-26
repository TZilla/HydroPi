from WebServer import WebServer as WS
from ControlModule.FanControl import FanControl as FC
from ControlModule.LightControl import LightControl as LC
from ControlModule.PumpControl import PumpControl as PC
from DBConn import DBConn as DB
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from WebServer import app

if __name__=='__main__':
	print("hello world")
	#app.run(debug=True)
	
	http_server = HTTPServer(WSGIContainer(app))
	http_server.listen(5000)
	IOLoop.instance().start()
	
	
