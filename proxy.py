import importlib
import logging
import struct

logging.basicConfig(level=logging.DEBUG)

import socket
import time

from socketserver import BaseRequestHandler, ThreadingTCPServer
ThreadingTCPServer.allow_reuse_address = True

from threading import Thread
import events

HOST = "127.0.0.1"
PORT = 43594

FORWARD_TO = '81.31.203.157' # "8.42.17.164"


def proxy_socket_thread(name, sock_in, sock_out, on_packet):
    while True:
        data = sock_in.recv(1024)
        result = on_packet(data, name)

        if result is not None:
            data = result

        sock_out.send(data)
        time.sleep(0.1)


class Proxy(BaseRequestHandler):
    def setup(self):
        print("[+] Accepted connection from: {}".format(self.client_address))
        print("[+] Forwarding connection to: {}".format((FORWARD_TO, PORT)))
        self.rs_server = socket.create_connection((FORWARD_TO, PORT))
        self.rs_client = self.request

    def handle(self):

        c_handshake = self.rs_client.recv(1)
        self.rs_server.send(c_handshake)

        if struct.unpack('b', c_handshake) == 14:
            s_nonce = self.rs_server.recv(8)
            self.rs_client.send(s_nonce)
            return

        threads = (
            Thread(target=proxy_socket_thread, kwargs={
                "name": "client",
                "sock_in": self.rs_client,
                "sock_out": self.rs_server,
                "on_packet": self.on_packet
            }),
            Thread(target=proxy_socket_thread, kwargs={
                "name": "server",
                "sock_in": self.rs_server,
                "sock_out": self.rs_client,
                "on_packet": self.on_packet
            }))

        for thread in threads:
            thread.start()

        while True:
            if all(t.is_alive() for t in threads):
                time.sleep(1)

    def on_packet(self, data, source):
        if not data:
            return

        try:
            if source == "client":
                events.on_client_packet(data)

            if source == "server":
                events.on_server_packet(data)

        except Exception as e:
            logging.error(e)


def run():
    with ThreadingTCPServer((HOST, PORT), RequestHandlerClass=Proxy) as sock:
        print(f"[+] Listening on: {HOST}:{PORT}")
        sock.serve_forever()
