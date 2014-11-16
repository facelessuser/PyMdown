import SimpleHTTPServer
import SocketServer
import sys

try:
    PORT = int(sys.argv[1])
except:
    PORT = 8080

Handler = SimpleHTTPServer.SimpleHTTPRequestHandler

httpd = SocketServer.TCPServer(("", PORT), Handler)

print("serving at port", PORT)
httpd.serve_forever()
