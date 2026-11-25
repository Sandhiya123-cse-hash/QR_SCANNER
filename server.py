import ssl
import socket
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

HOST = "0.0.0.0"
PORT = 8443

folder = Path(__file__).resolve().parent

class QRHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(folder), **kwargs)

server = HTTPServer((HOST, PORT), QRHandler)

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(
    certfile=str(folder / "cert.pem"),
    keyfile=str(folder / "key.pem")
)

server.socket = context.wrap_socket(
    server.socket,
    server_side=True
)

print("Rotation QR server started.")
print("Open qr_display.html on your laptop.")
print(f"Server port: {PORT}")
print("Stop server with CTRL + C")

server.serve_forever()