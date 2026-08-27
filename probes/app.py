from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import threading
import random

READY = False
CRASH = False

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global READY, CRASH
        if self.path == "/healthz":  # startup + liveness
            if CRASH:
                # Simulate crash
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b"Crash!")
            else:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Alive")
        elif self.path == "/ready":   # readiness
            if READY:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Ready")
            else:
                self.send_response(503)
                self.end_headers()
                self.wfile.write(b"Starting")
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Hello World!")

def slow_start():
    global READY
    time.sleep(20)  # simulate slow startup
    READY = True

def random_crash():
    global CRASH
    while True:
        time.sleep(30)
        if random.random() < 0.2:  # 20% chance every 30s
            CRASH = True
            time.sleep(10)  # stay crashed for 10s
            CRASH = False

threading.Thread(target=slow_start).start()
threading.Thread(target=random_crash).start()

server = HTTPServer(("0.0.0.0", 8080), Handler)
server.serve_forever()
