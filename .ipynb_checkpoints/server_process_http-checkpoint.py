from socket import *
import socket
import time
import sys
import logging
import multiprocessing
import threading
from http import HttpServer

httpserver = HttpServer()


class ProcessTheClient(threading.Thread):
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address
        multiprocessing.Process.__init__(self)

    def run(self):
        rcv = ""
        while True:
            try:
                data = self.connection.recv(32)
                if data:
                    # merubah input dari socket (berupa bytes) ke dalam string
                    # agar bisa mendeteksi \r\n
                    d = data.decode()
                    rcv = rcv + d
                    if rcv[-2:] == '\r\n':
                        # end of command, proses string
                        logging.warning("data dari client: {}" . format(rcv))
                        hasil = httpserver.proses(rcv)
                        # hasil akan berupa bytes
                        # untuk bisa ditambahi dengan string, maka string harus di encode
                        hasil = hasil.encode()
                        logging.warning("balas ke  client: {}" . format(hasil))
                        # hasil sudah dalam bentuk bytes
                        self.connection.sendall(hasil)
                        rcv = ""
                        self.connection.close()
                        break
                else:
                    break
            except OSError as e:
                pass
        self.connection.close()


class Server(multiprocessing.Process):
    def __init__(self):
        self.the_clients = []
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        multiprocessing.Process.__init__(self)

    def run(self):
        self.my_socket.bind(('0.0.0.0', 8889))
        self.my_socket.listen(1)
        while True:
            self.connection, self.client_address = self.my_socket.accept()
            logging.warning("connection from {}".format(self.client_address))

            clt = ProcessTheClient(self.connection, self.client_address)
            clt.start()
            self.the_clients.append(clt)


def main():
    svr = Server()
    svr.start()


if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("-t", "--thread", dest="thread_count",
                        help="Number of threads (default 1)", default=1)
    parser.add_argument("-p", "--port", dest="port",
                        help="Port to listen to (default 8889)", default=8889)

    args = parser.parse_args()
    port = int(args.port)
    thread_count = int(args.thread_count)

    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serversocket.bind(('0.0.0.0', port))
    serversocket.listen(5)

    logging.warning("server started")

    for i in range(thread_count):
        logging.warning("thread "+str(i)+" ready")
        svr = Server()
        svr.start()

    while True:
        logging.warning("main thread listening")
        clientsocket, address = serversocket.accept()
        logging.warning("accepted connection from {}".format(address))
        client_handler = ProcessTheClient(clientsocket, address)
        client_handler.start()
