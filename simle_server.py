from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO

import ssl

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello, world!')
        print('test get')

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        print("test post")
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()
        response = BytesIO()
        response.write(b'This is POST request. ')
        response.write(b'Received: ')
        response.write(body)
        self.wfile.write(response.getvalue())


httpd = HTTPServer(('0.0.0.0', 1081), SimpleHTTPRequestHandler)

httpd.socket = ssl.wrap_socket(httpd.socket,
        keyfile="server.key",
        certfile='server.crt', server_side=True)



httpd.serve_forever()
