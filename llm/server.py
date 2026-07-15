from http.server import HTTPServer, BaseHTTPRequestHandler

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Hello, World!")

host = "127.0.0.1"
port = 8000

server = HTTPServer((host, port), MyHandler)
print(f"Server is running on http://{host}:{port}")